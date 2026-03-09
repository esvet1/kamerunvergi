import tkinter as tk
from tkinter import ttk


class ProductRow:
    def __init__(self, parent, index, on_change, on_remove, theme):
        self.parent = parent
        self.index = index
        self.on_change = on_change
        self.on_remove = on_remove
        self.theme = theme

        self.name_var = tk.StringVar()
        self.fob_var = tk.StringVar(value="0")

        self.name_var.trace_add("write", lambda *_: self.on_change())
        self.fob_var.trace_add("write", lambda *_: self.on_change())

        self.name_entry = ttk.Entry(parent, textvariable=self.name_var)
        self.fob_entry = ttk.Entry(parent, textvariable=self.fob_var, justify="right")
        self.remove_btn = ttk.Button(parent, text="Remove", command=self.remove)

    def render(self, row_index):
        self.name_entry.grid(row=row_index, column=0, sticky="ew", padx=(0, 8), pady=4)
        self.fob_entry.grid(row=row_index, column=1, sticky="ew", padx=(0, 8), pady=4)
        self.remove_btn.grid(row=row_index, column=2, sticky="ew", pady=4)

    def remove(self):
        self.destroy()
        self.on_remove(self)

    def destroy(self):
        self.name_entry.destroy()
        self.fob_entry.destroy()
        self.remove_btn.destroy()

    def get_data(self):
        name = self.name_var.get().strip() or f"Product {self.index + 1}"
        fob = safe_float(self.fob_var.get())
        return name, fob


class CustomsValuationCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Customs Valuation Calculator")
        self.geometry("1180x760")
        self.minsize(980, 620)

        self.is_dark = tk.BooleanVar(value=False)

        self.freight_var = tk.StringVar(value="0")
        self.insurance_var = tk.StringVar(value="0")
        self.exchange_var = tk.StringVar(value="1")
        self.duty_var = tk.StringVar(value="0")
        self.tva_var = tk.StringVar(value="0")
        self.additional_var = tk.StringVar(value="0")

        self.result_total_fob = tk.StringVar(value="0.00")
        self.result_cif = tk.StringVar(value="0.00")
        self.result_customs_total = tk.StringVar(value="0.00")
        self.result_tax_total = tk.StringVar(value="0.00")

        self.rows = []
        self.result_labels = []

        self.style = ttk.Style(self)
        self._init_styles()
        self._build_ui()
        self.apply_theme()

        for var in [
            self.freight_var,
            self.insurance_var,
            self.exchange_var,
            self.duty_var,
            self.tva_var,
            self.additional_var,
        ]:
            var.trace_add("write", lambda *_: self.calculate())

        self.add_row("Product 1", "0")

    def _init_styles(self):
        self.style.configure("Header.TLabel", font=("Segoe UI", 11, "bold"))
        self.style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"))
        self.style.configure("Card.TLabelframe", padding=12)
        self.style.configure("Card.TLabelframe.Label", font=("Segoe UI", 10, "bold"))

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        header = ttk.Frame(self)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=16, pady=(16, 8))
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Customs Valuation Calculator", style="Title.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Checkbutton(
            header,
            text="Dark mode",
            variable=self.is_dark,
            command=self.apply_theme,
        ).grid(row=0, column=1, sticky="e")

        left = ttk.LabelFrame(self, text="Products", style="Card.TLabelframe")
        left.grid(row=1, column=0, sticky="nsew", padx=(16, 8), pady=8)
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        table_container = ttk.Frame(left)
        table_container.grid(row=0, column=0, sticky="nsew")
        table_container.columnconfigure(0, weight=2)
        table_container.columnconfigure(1, weight=1)
        table_container.columnconfigure(2, weight=0)

        ttk.Label(table_container, text="Product name", style="Header.TLabel").grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=(0, 6)
        )
        ttk.Label(table_container, text="FOB USD", style="Header.TLabel").grid(
            row=0, column=1, sticky="e", padx=(0, 8), pady=(0, 6)
        )

        self.rows_frame = ttk.Frame(left)
        self.rows_frame.grid(row=1, column=0, sticky="nsew", pady=(4, 8))
        self.rows_frame.columnconfigure(0, weight=2)
        self.rows_frame.columnconfigure(1, weight=1)
        self.rows_frame.columnconfigure(2, weight=0)

        actions = ttk.Frame(left)
        actions.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        actions.columnconfigure(0, weight=1)

        ttk.Button(actions, text="Add product", command=lambda: self.add_row()).grid(
            row=0, column=0, sticky="w"
        )

        right = ttk.Frame(self)
        right.grid(row=1, column=1, sticky="nsew", padx=(8, 16), pady=8)
        right.rowconfigure(2, weight=1)
        right.columnconfigure(0, weight=1)

        globals_frame = ttk.LabelFrame(right, text="Global Inputs", style="Card.TLabelframe")
        globals_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        globals_frame.columnconfigure(1, weight=1)

        self._labeled_entry(globals_frame, "Freight USD", self.freight_var, 0)
        self._labeled_entry(globals_frame, "Insurance USD", self.insurance_var, 1)
        self._labeled_entry(globals_frame, "Exchange rate", self.exchange_var, 2)
        self._labeled_entry(globals_frame, "Duty %", self.duty_var, 3)
        self._labeled_entry(globals_frame, "TVA %", self.tva_var, 4)
        self._labeled_entry(globals_frame, "Additional tax %", self.additional_var, 5)

        totals_frame = ttk.LabelFrame(right, text="Totals", style="Card.TLabelframe")
        totals_frame.grid(row=1, column=0, sticky="ew", pady=8)
        totals_frame.columnconfigure(1, weight=1)

        self._result_row(totals_frame, "Total FOB (USD)", self.result_total_fob, 0)
        self._result_row(totals_frame, "CIF (USD)", self.result_cif, 1)
        self._result_row(totals_frame, "Total customs value (local)", self.result_customs_total, 2)
        self._result_row(totals_frame, "Total tax (local)", self.result_tax_total, 3)

        details_frame = ttk.LabelFrame(right, text="Per Product Results", style="Card.TLabelframe")
        details_frame.grid(row=2, column=0, sticky="nsew", pady=(8, 0))
        details_frame.rowconfigure(0, weight=1)
        details_frame.columnconfigure(0, weight=1)

        columns = (
            "name",
            "fob",
            "ratio",
            "cif",
            "custom_value",
            "duty",
            "additional",
            "tva",
            "total_tax",
        )
        self.tree = ttk.Treeview(details_frame, columns=columns, show="headings", height=10)
        self.tree.grid(row=0, column=0, sticky="nsew")

        headings = {
            "name": "Product",
            "fob": "FOB USD",
            "ratio": "Ratio",
            "cif": "Product CIF USD",
            "custom_value": "Custom value",
            "duty": "Duty",
            "additional": "Additional",
            "tva": "TVA",
            "total_tax": "Total tax",
        }

        widths = {
            "name": 150,
            "fob": 90,
            "ratio": 70,
            "cif": 110,
            "custom_value": 120,
            "duty": 90,
            "additional": 95,
            "tva": 90,
            "total_tax": 100,
        }

        for col in columns:
            self.tree.heading(col, text=headings[col])
            anchor = "w" if col == "name" else "e"
            self.tree.column(col, width=widths[col], anchor=anchor)

        scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def _labeled_entry(self, parent, label, variable, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=(0, 8), pady=4)
        entry = ttk.Entry(parent, textvariable=variable, justify="right")
        entry.grid(row=row, column=1, sticky="ew", pady=4)

    def _result_row(self, parent, label, variable, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=(0, 8), pady=4)
        value_label = ttk.Label(parent, textvariable=variable, style="Header.TLabel")
        value_label.grid(row=row, column=1, sticky="e", pady=4)
        self.result_labels.append(value_label)

    def add_row(self, name="", fob="0"):
        row = ProductRow(
            self.rows_frame,
            len(self.rows),
            on_change=self.calculate,
            on_remove=self.remove_row,
            theme=self,
        )
        row.name_var.set(name)
        row.fob_var.set(fob)
        self.rows.append(row)
        self.relayout_rows()
        self.calculate()

    def remove_row(self, row):
        if row in self.rows:
            self.rows.remove(row)
        for idx, item in enumerate(self.rows):
            item.index = idx
        self.relayout_rows()
        self.calculate()

    def relayout_rows(self):
        for idx, row in enumerate(self.rows, start=0):
            row.render(idx)

    def apply_theme(self):
        dark = self.is_dark.get()

        if dark:
            bg = "#151A21"
            card_bg = "#1E2530"
            fg = "#E7ECF3"
            entry_bg = "#273141"
            accent = "#9BB8FF"
        else:
            bg = "#F3F5F8"
            card_bg = "#FFFFFF"
            fg = "#1D2733"
            entry_bg = "#FFFFFF"
            accent = "#2D5BE3"

        self.style.theme_use("clam")
        self.configure(bg=bg)
        self.style.configure("TFrame", background=bg)
        self.style.configure("TLabelframe", background=card_bg, foreground=fg, borderwidth=1)
        self.style.configure("TLabelframe.Label", background=card_bg, foreground=fg)
        self.style.configure("TLabel", background=bg, foreground=fg)
        self.style.configure("Title.TLabel", background=bg, foreground=accent)
        self.style.configure("Header.TLabel", background=card_bg, foreground=fg)
        self.style.configure("TEntry", fieldbackground=entry_bg, foreground=fg, borderwidth=1)
        self.style.configure("TButton", background=card_bg, foreground=fg)
        self.style.map("TButton", background=[("active", accent)], foreground=[("active", "#FFFFFF")])
        self.style.configure("TCheckbutton", background=bg, foreground=fg)
        self.style.map("TCheckbutton", background=[("active", bg)], foreground=[("active", fg)])

        tree_bg = card_bg
        tree_fg = fg
        self.style.configure(
            "Treeview",
            background=tree_bg,
            foreground=tree_fg,
            fieldbackground=tree_bg,
            bordercolor=card_bg,
        )
        self.style.configure("Treeview.Heading", background=bg, foreground=fg)
        self.style.map("Treeview", background=[("selected", accent)], foreground=[("selected", "#FFFFFF")])

        for label in self.result_labels:
            label.configure(style="Header.TLabel")

    def calculate(self):
        product_data = [r.get_data() for r in self.rows]

        total_fob = sum(fob for _, fob in product_data)
        freight = safe_float(self.freight_var.get())
        insurance = safe_float(self.insurance_var.get())
        exchange_rate = safe_float(self.exchange_var.get())
        duty_percent = safe_float(self.duty_var.get()) / 100.0
        tva_percent = safe_float(self.tva_var.get()) / 100.0
        additional_percent = safe_float(self.additional_var.get()) / 100.0

        cif = total_fob + freight + insurance

        self.tree.delete(*self.tree.get_children())

        total_custom_value = 0.0
        total_tax = 0.0

        for name, product_fob in product_data:
            ratio = (product_fob / total_fob) if total_fob > 0 else 0.0
            product_cif = ratio * cif
            custom_value = product_cif * exchange_rate
            duty = custom_value * duty_percent
            additional = custom_value * additional_percent
            tva = (custom_value + duty + additional) * tva_percent
            product_total_tax = duty + additional + tva

            total_custom_value += custom_value
            total_tax += product_total_tax

            self.tree.insert(
                "",
                "end",
                values=(
                    name,
                    money(product_fob),
                    percent(ratio),
                    money(product_cif),
                    money(custom_value),
                    money(duty),
                    money(additional),
                    money(tva),
                    money(product_total_tax),
                ),
            )

        self.result_total_fob.set(money(total_fob))
        self.result_cif.set(money(cif))
        self.result_customs_total.set(money(total_custom_value))
        self.result_tax_total.set(money(total_tax))


def safe_float(value):
    try:
        text = str(value).strip()
        if not text:
            return 0.0
        normalized = text.replace(",", "")
        return float(normalized)
    except (TypeError, ValueError):
        return 0.0


def money(value):
    return f"{value:,.2f}"


def percent(value):
    return f"{value * 100:,.2f}%"


if __name__ == "__main__":
    app = CustomsValuationCalculator()
    app.mainloop()
