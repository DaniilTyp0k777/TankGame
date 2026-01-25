import json
import socket
import threading
from typing import Optional


HOST = "0.0.0.0"
PORT = 5000


def _send_json(sock: socket.socket, obj: dict) -> None:
    data = (json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8")
    sock.sendall(data)


def _recv_lines(sock: socket.socket, buffer: bytearray) -> list[str]:
    try:
        chunk = sock.recv(4096)
    except OSError:
        return []
    if not chunk:
        return []
    buffer.extend(chunk)
    lines: list[str] = []
    while True:
        idx = buffer.find(b"\n")
        if idx == -1:
            break
        line = buffer[:idx]
        del buffer[: idx + 1]
        try:
            lines.append(line.decode("utf-8"))
        except UnicodeDecodeError:
            continue
    return lines


class PlayerConn:
    def __init__(self, sock: socket.socket, addr: tuple[str, int]):
        self.sock = sock
        self.addr = addr
        self.buffer = bytearray()
        self.room: Optional["Room"] = None
        self.alive = True

    def close(self) -> None:
        self.alive = False
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            self.sock.close()
        except OSError:
            pass


class Room:
    def __init__(self, p1: PlayerConn, p2: PlayerConn, seed: int):
        self.p1 = p1
        self.p2 = p2
        self.seed = seed
        self.lock = threading.Lock()

    def other(self, p: PlayerConn) -> PlayerConn:
        return self.p2 if p is self.p1 else self.p1


_waiting_lock = threading.Lock()
_waiting: Optional[PlayerConn] = None
_seed_counter = 1000


def _next_seed() -> int:
    global _seed_counter
    _seed_counter += 1
    return _seed_counter


def _matchmake(p: PlayerConn) -> None:
    global _waiting

    with _waiting_lock:
        if _waiting is None:
            _waiting = p
            _send_json(p.sock, {"type": "status", "state": "searching"})
            return

        opponent = _waiting
        _waiting = None

    seed = _next_seed()
    room = Room(opponent, p, seed)
    opponent.room = room
    p.room = room

    _send_json(opponent.sock, {"type": "match", "role": 1, "seed": seed})
    _send_json(p.sock, {"type": "match", "role": 2, "seed": seed})


def _handle_client(p: PlayerConn) -> None:
    try:
        _send_json(p.sock, {"type": "hello", "server": "tanks-match", "version": 1})
        _matchmake(p)

        while p.alive:
            lines = _recv_lines(p.sock, p.buffer)
            if not lines:
                break

            for line in lines:
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if msg.get("type") == "ping":
                    _send_json(p.sock, {"type": "pong"})
                    continue

                room = p.room
                if room is None:
                    if msg.get("type") == "search":
                        _matchmake(p)
                    continue

                other = room.other(p)
                if not other.alive:
                    continue

                msg["from"] = 1 if p is room.p1 else 2
                _send_json(other.sock, msg)

    except (ConnectionError, OSError):
        pass
    finally:
        room = p.room
        p.close()

        if room is not None:
            other = room.other(p)
            try:
                _send_json(other.sock, {"type": "opponent_left"})
            except OSError:
                pass

        global _waiting
        with _waiting_lock:
            if _waiting is p:
                _waiting = None


def serve_forever(host: str = HOST, port: int = PORT) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen()
        print(f"[SERVER] Listening on {host}:{port}")

        while True:
            client_sock, addr = s.accept()
            client_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            p = PlayerConn(client_sock, addr)
            t = threading.Thread(target=_handle_client, args=(p,), daemon=True)
            t.start()


if __name__ == "__main__":
    serve_forever()
