import tkinter as tk
from tkinter import messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading
import time

class DFA_GUI:
    #initializes the tkinter interface
    def __init__(self, root):
        self.root = root
        self.root.title("DFA Creator")

        self.alphabet = []
        self.states = []
        self.start_state = None
        self.accept_states = []
        self.transitions = {}

        self.create_widgets()

    # Creates tkinter widgets
    def create_widgets(self):
        tk.Label(self.root, text="Alphabet (comma-separated):").grid(row=0, column=0, sticky="w")
        self.alphabet_entry = tk.Entry(self.root, width=30)
        self.alphabet_entry.grid(row=0, column=1)

        tk.Label(self.root, text="States (comma-separated):").grid(row=1, column=0, sticky="w")
        self.states_entry = tk.Entry(self.root, width=30)
        self.states_entry.grid(row=1, column=1)

        tk.Label(self.root, text="Start State:").grid(row=2, column=0, sticky="w")
        self.start_state_entry = tk.Entry(self.root, width=30)
        self.start_state_entry.grid(row=2, column=1)

        tk.Label(self.root, text="Accept States (comma-separated):").grid(row=3, column=0, sticky="w")
        self.accept_states_entry = tk.Entry(self.root, width=30)
        self.accept_states_entry.grid(row=3, column=1)

        tk.Button(self.root, text="Define Transitions", command=self.define_transitions).grid(row=4, column=0, pady=10)
        tk.Button(self.root, text="Validate DFA", command=self.validate_dfa).grid(row=4, column=1, pady=10)

        tk.Label(self.root, text="Input String to Simulate:").grid(row=5, column=0, sticky="w")
        self.simulation_entry = tk.Entry(self.root, width=30)
        self.simulation_entry.grid(row=5, column=1)

        tk.Button(self.root, text="Simulate String", command=self.simulate_string).grid(row=6, column=0, columnspan=2, pady=10)

    # creates the transition table
    def define_transitions(self):
        try:
            self.alphabet = [x.strip() for x in self.alphabet_entry.get().split(",")]
            self.states = [x.strip() for x in self.states_entry.get().split(",")]
            self.start_state = self.start_state_entry.get().strip()
            self.accept_states = [x.strip() for x in self.accept_states_entry.get().split(",")]

            if not self.alphabet or not self.states or not self.start_state:
                raise ValueError("Alphabet, states, and start state cannot be empty.")

            if self.start_state not in self.states:
                raise ValueError("Start state must be a valid state.")

            for state in self.accept_states:
                if state not in self.states:
                    raise ValueError(f"Accept state '{state}' is not a valid state.")

            self.transition_window = tk.Toplevel(self.root)
            self.transition_window.title("Transition Table")

            tk.Label(self.transition_window, text="State").grid(row=0, column=0, padx=5, pady=5)
            for col, symbol in enumerate(self.alphabet, start=1):
                tk.Label(self.transition_window, text=symbol).grid(row=0, column=col, padx=5, pady=5)

            self.transition_entries = {}
            for row, state in enumerate(self.states, start=1):
                tk.Label(self.transition_window, text=state).grid(row=row, column=0, padx=5, pady=5)
                for col, symbol in enumerate(self.alphabet, start=1):
                    entry = tk.Entry(self.transition_window, width=10)
                    entry.grid(row=row, column=col, padx=5, pady=5)
                    self.transition_entries[(state, symbol)] = entry

            tk.Button(self.transition_window, text="Save Transitions", command=self.save_transitions).grid(
                row=len(self.states) + 1, column=0, columnspan=len(self.alphabet) + 1, pady=10
            )
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    # Saves the transitions defined in the transition table
    def save_transitions(self):
        try:
            self.transitions = {state: {} for state in self.states}
            for (state, symbol), entry in self.transition_entries.items():
                to_state = entry.get().strip()
                if to_state not in self.states:
                    raise ValueError(f"Invalid transition: {state} --{symbol}--> {to_state}")
                self.transitions[state][symbol] = to_state

            messagebox.showinfo("Success", "Transitions saved successfully.")
            self.transition_window.destroy()
        except ValueError as e:
            messagebox.showerror("Transition Error", str(e))

    # Validates if the DFA is valid or not
    def validate_dfa(self):
        try:
            for state in self.states:
                for symbol in self.alphabet:
                    if self.transitions[state].get(symbol) is None:
                        raise ValueError(f"Missing transition for state '{state}' on input '{symbol}'.")
            messagebox.showinfo("Validation", "The DFA is valid!")
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))

    # Checks if the transitions are defined and correct, 
    # and initializes the simulation of the string once everything is correct.
    def simulate_string(self):
        try:
            input_string = self.simulation_entry.get().strip()
            if not self.transitions:
                raise ValueError("Transitions are not defined. Please define them first.")

            current_state = self.start_state
            path = [current_state]

            for symbol in input_string:
                if symbol not in self.alphabet:
                    raise ValueError(f"Symbol '{symbol}' is not in the alphabet.")
                current_state = self.transitions[current_state][symbol]
                path.append(current_state)

            self.visualize_simulation(path, input_string)
            self.check_acceptance(path)
        except ValueError as e:
            messagebox.showerror("Simulation Error", str(e))

    # Outputs whether or not the string is accepted or rejected after the simulation.
    def check_acceptance(self, path):
        final_state = path[-1]
        if final_state in self.accept_states:
            messagebox.showinfo("Result", f"The string is accepted! Final state: {final_state}")
        else:
            messagebox.showinfo("Result", f"The string is rejected. Final state: {final_state}")

    # Simulation of the String
    def visualize_simulation(self, path, input_string):
        G = nx.DiGraph()
        for state in self.states:
            G.add_node(state, color="green" if state in self.accept_states else "blue")
        for state, transitions in self.transitions.items():
            for symbol, to_state in transitions.items():
                G.add_edge(state, to_state, label=symbol)

        pos = nx.spring_layout(G)

        fig, ax = plt.subplots(figsize=(8, 6))
        colors = [G.nodes[node]['color'] for node in G.nodes]

        def update(frame):
            ax.clear()
            nx.draw(G, pos, with_labels=True, node_color=colors, ax=ax, node_size=1500, font_size=10)
            edge_labels = nx.get_edge_attributes(G, 'label')
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)

            # Draw the current node in red
            current_node = path[frame]
            nx.draw_networkx_nodes(G, pos, nodelist=[current_node], node_color="red", ax=ax, node_size=1500)

            # Add a legend
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor="green", edgecolor="black", label="Accept State"),
                Patch(facecolor="blue", edgecolor="black", label="State"),
                Patch(facecolor="red", edgecolor="black", label="Current State"),
            ]
            ax.legend(handles=legend_elements, loc="upper right")

            # If this is the last frame, add a delay before showing the result
            if frame == len(path) - 1:
                threading.Thread(target=self.delayed_check_acceptance, args=(path,), daemon=True).start()

        def on_close(event):
            self.animation_interrupted = True  # Mark animation as interrupted
            plt.close(fig)

        fig.canvas.mpl_connect("close_event", on_close)

        ani = FuncAnimation(fig, update, frames=len(path), interval=1000, repeat=False)

        plt.suptitle(f"Simulation of Input String: {input_string}")
        plt.show()



if __name__ == "__main__":
    root = tk.Tk()
    app = DFA_GUI(root)
    root.mainloop()
