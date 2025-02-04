import tkinter as tk
from tkinter import ttk
import requests
from tkinter import messagebox
import asyncio
import threading


async def fetch_and_display_data(api_key):
    loop = asyncio.get_event_loop()
    try:
        response = await loop.run_in_executor(None, requests.get, api_key)
        if response.status_code == 200:
            data = response.json()
            if not data:
                return {'players': [], 'point_votes': []}
            total_point_votes_list = data["SessionStats"]["PointVotes"]
            player_list_with_votes = data.get('Players', [])
            return {
                'players': player_list_with_votes,
                'point_votes': total_point_votes_list[:5],  # Limit to 5 records
            }
        else:
            messagebox.showerror("Error", f"API call failed with status code: {response.status_code}")
            return {'players': [], 'point_votes': []}
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch data: {e}")
        return {'players': [], 'point_votes': []}


def update_table(data):
    for row in table.get_children():
        table.delete(row)

    for player in data['players']:
        player_name = player.get('Name')
        player_points = "-" if player.get('IsObserver') else player.get('Points')

        row_id = table.insert("", "end", values=(player_name, player_points))
        table.item(row_id, tags=("green_row",))

    if not data['players']:
        table.insert("", "end", values=("NO DATA", ""), tags=("green_row",))

    update_point_votes(data['point_votes'])


def update_point_votes(point_votes):
    for row in point_vote_table.get_children():
        point_vote_table.delete(row)

    for vote in point_votes:
        points = vote.get("Points", 'N/A') 
        votes = vote.get("Votes", 0)
        row_id = point_vote_table.insert("", "end", values=(points, votes))
        point_vote_table.item(row_id, tags=("red_row",))


async def refresh_data_periodically():
    api_key = api_entry.get()
    fetch_button.config(text="Data fetching")
    if api_key.strip():
        player_data = await fetch_and_display_data(api_key)
        update_table(player_data)
    else:
        messagebox.showwarning("Warning", "Please enter the API key.")
    fetch_button.config(text="Fetch Data")
    app.after(3000, lambda: threading.Thread(target=asyncio.run, args=(refresh_data_periodically(),)).start())


def start_async_loop():
    asyncio.run(refresh_data_periodically())


# Initialize UI
app = tk.Tk()
app.title("Bloody Cheaters")
app.geometry("900x500")

# Top Frame for API input
top_frame = tk.Frame(app)
top_frame.pack(pady=10, fill="x")

api_label = tk.Label(top_frame, text="API Key:")
api_label.pack(side="left", padx=5)
api_entry = tk.Entry(top_frame, width=50)
api_entry.pack(side="left", padx=5)
fetch_button = tk.Button(top_frame, text="Fetch Data", command=lambda: threading.Thread(target=start_async_loop).start())
fetch_button.pack(side="left", padx=5)

# Main Table (70% of UI)
table_frame = tk.Frame(app, height=350)  # Takes 70% space
table_frame.pack(fill="both", expand=True, padx=10, pady=10)

scroll_player = tk.Scrollbar(table_frame, orient="vertical")
scroll_player.pack(side="right", fill="y")

style = ttk.Style()
style.configure("Treeview.Heading", font=("Arial", 10, "bold"), foreground="black")
style.configure("Treeview", font=("Arial", 10))

columns = ("Name", "Points")
table = ttk.Treeview(table_frame, columns=columns, show="headings", yscrollcommand=scroll_player.set, style="Treeview")

table.heading("Name", text="Name")
table.heading("Points", text="Points")
table.column("Name", width=200, anchor="center")
table.column("Points", width=100, anchor="center")
table.pack(side="left", fill="both", expand=True)

table.tag_configure("green_row", background="lightgreen")

scroll_player.config(command=table.yview)

# Point Votes Table (30% of UI)
point_vote_frame = tk.Frame(app, height=150)  # Takes 30% space
point_vote_frame.pack(fill="x", padx=10, pady=5)

point_vote_scrollbar = tk.Scrollbar(point_vote_frame, orient="vertical")
point_vote_scrollbar.pack(side="right", fill="y")

point_vote_columns = ("Points", "Votes")
point_vote_table = ttk.Treeview(point_vote_frame, columns=point_vote_columns, show="headings", yscrollcommand=point_vote_scrollbar.set)

point_vote_table.heading("Points", text="Points")
point_vote_table.heading("Votes", text="Votes")
point_vote_table.column("Points", width=100, anchor="center")
point_vote_table.column("Votes", width=100, anchor="center")
point_vote_table.pack(side="left", fill="both", expand=True)

point_vote_table.tag_configure("red_row", background="lightcoral")

point_vote_scrollbar.config(command=point_vote_table.yview)

app.mainloop()
