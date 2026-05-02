from fastapi import FastAPI, WebSocket

@app.get("/")
def home():
    return {"message": "Backend is running 🚀"}

app = FastAPI()

rooms = {}

class Room:
    def __init__(self):
        self.players = []
        self.choices = {}
        self.batsman = None
        self.bowler = None
        self.score = 0

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()

    if room_id not in rooms:
        rooms[room_id] = Room()

    room = rooms[room_id]
    room.players.append(websocket)

    # Start game when 2 players join
    if len(room.players) == 2:
        room.batsman = room.players[0]
        room.bowler = room.players[1]

        for player in room.players:
            await player.send_json({"msg": "Game Start"})

    while True:
        data = await websocket.receive_json()
        room.choices[websocket] = data["number"]

        if len(room.choices) == 2:
            batsman_choice = room.choices[room.batsman]
            bowler_choice = room.choices[room.bowler]

            if batsman_choice == bowler_choice:
                result = "OUT"
                room.batsman, room.bowler = room.bowler, room.batsman
            else:
                room.score += batsman_choice
                result = f"Score: {room.score}"

            for player in room.players:
                await player.send_json({
                    "batsman": batsman_choice,
                    "bowler": bowler_choice,
                    "result": result
                })

            room.choices = {}