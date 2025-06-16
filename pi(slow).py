import tkinter as tk
from tkinter import ttk
from decimal import Decimal, getcontext
import threading
import time

def compute_pi_chudnovsky(digits, progress_callback, done_callback):
    getcontext().prec = digits + 5
    C = 426880 * Decimal(10005).sqrt()
    M = 1
    L = 13591409
    X = 1
    K = 6
    S = L

    start_time = time.time()

    for i in range(1, digits):
        M = (M * (K ** 3 - 16 * K)) // (i ** 3)
        L += 545140134
        X *= -262537412640768000
        term = Decimal(M * L) / X
        S += term
        K += 12

        if i % 100 == 0 or i == 1 or i == digits - 1:
            elapsed = time.time() - start_time
            avg_time_per_step = elapsed / i
            remaining_steps = digits - i
            estimated_remaining = avg_time_per_step * remaining_steps

            pi_partial = str(C / S)[:i + 2]
            last_digits = pi_partial[-10:] if len(pi_partial) >= 10 else pi_partial

            progress_callback(i, last_digits, estimated_remaining)

            if i % 200 == 0:
                with open("pi2.txt", "w") as f:
                    f.write(pi_partial + "\n")

    pi_final = str(+C / S)[:digits + 2]
    done_callback(pi_final)

def start_gui():
    def start_calculation():
        try:
            digits = int(entry.get())
        except ValueError:
            progress_label.config(text="Enter a valid integer.")
            return

        if digits < 10:
            progress_label.config(text="Enter at least 10 digits.")
            return

        start_button.config(state="disabled")
        progress_label.config(text="Starting...")
        output_text.delete("1.0", tk.END)
        progress_bar["maximum"] = digits
        progress_bar["value"] = 0
        last_digits_var.set("")
        eta_var.set("")

        def run():
            def progress_callback(i, last_10, eta_seconds):
                root.after(0, lambda: update_ui(i, last_10, eta_seconds))

            def done_callback(result):
                def finish():
                    progress_label.config(text="Done! π saved to pi.txt")
                    output_text.delete("1.0", tk.END)
                    output_text.insert(tk.END, result)
                    with open("pi.txt", "w") as f:
                        f.write(result + "\n")
                    start_button.config(state="normal")
                    eta_var.set("Finished!")
                root.after(0, finish)

            compute_pi_chudnovsky(digits, progress_callback, done_callback)

        threading.Thread(target=run, daemon=True).start()

    def update_ui(i, last_10, eta_seconds):
        progress_label.config(text=f"Calculating... ({i}/{int(progress_bar['maximum'])})")
        progress_bar["value"] = i
        last_digits_var.set(last_10)
        eta_var.set(f"~{int(eta_seconds)}s remaining")

    root = tk.Tk()
    root.title("π Calculator (Chudnovsky)")

    tk.Label(root, text="Number of digits:").pack(pady=5)
    entry = tk.Entry(root)
    entry.insert(0, "100")
    entry.pack(pady=5)

    start_button = tk.Button(root, text="Calculate π", command=start_calculation)
    start_button.pack(pady=5)

    progress_label = tk.Label(root, text="Waiting...")
    progress_label.pack()

    progress_bar = ttk.Progressbar(root, length=400, mode='determinate')
    progress_bar.pack(pady=5)

    tk.Label(root, text="Last 10 Digits:").pack()
    last_digits_var = tk.StringVar()
    last_digits_label = tk.Label(root, textvariable=last_digits_var, font=("Courier", 14))
    last_digits_label.pack(pady=5)

    tk.Label(root, text="Estimated Time Remaining:").pack()
    eta_var = tk.StringVar()
    eta_label = tk.Label(root, textvariable=eta_var)
    eta_label.pack(pady=5)

    output_text = tk.Text(root, height=10, width=80)
    output_text.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    start_gui()
