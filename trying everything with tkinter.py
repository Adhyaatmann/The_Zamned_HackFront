from datetime import datetime
import os
import psycopg2
from dotenv import load_dotenv
from customtkinter import *
from PIL import Image
from gemini_analyzer import get_commitments_from_gemini

# ==========================================
# LOAD ENVIRONMENT & DATABASE
# ==========================================
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
connection = psycopg2.connect(DATABASE_URL)
cursor = connection.cursor()

app = CTk()
app.geometry("1100x700")
app.title("The Missing Rupee - Financial Discovery & Anti-Dark Patterns")

# Configure main window grid
app.grid_columnconfigure(1, weight=1)
app.grid_rowconfigure(0, weight=1)

# ==========================================
# FETCH COMMITMENTS DATA
# ==========================================
try:
    commitments_data = get_commitments_from_gemini()
except Exception:
    commitments_data = []

# Fallback sample data if DB or Gemini call fails
if not commitments_data:
    commitments_data = [
        {
            "name": "Netflix",
            "frequency": "monthly",
            "category": "Entertainment",
            "amount": "₹799",
            "date": "2025-08-15",
            "initial": "N",
            "bg": "#FEE2E2",
            "payment_mechanism": "Card recurring",
            "cancellation_steps": [
                "Open Netflix.com in your web browser and log into your account.",
                "Click your profile icon in the top right corner and select 'Account'.",
                "Under the 'Membership & Billing' section, click the 'Cancel Membership' button.",
                "Click 'Finish Cancellation' to stop future automatic debits.",
            ],
            "history": [
                {
                    "date": "2025-03-15",
                    "description": "ACH DEBIT PAYPAL *NETFLIX",
                    "amount": "₹649",
                },
                {
                    "date": "2025-04-15",
                    "description": "ACH DEBIT PAYPAL *NETFLIX",
                    "amount": "₹649",
                },
                {
                    "date": "2025-05-15",
                    "description": "ACH DEBIT PAYPAL *NETFLIX",
                    "amount": "₹649",
                },
                {
                    "date": "2025-06-15",
                    "description": "ACH DEBIT PAYPAL *NETFLIX",
                    "amount": "₹649",
                },
                {
                    "date": "2025-07-15",
                    "description": "ACH DEBIT PAYPAL *NETFLIX",
                    "amount": "₹799",
                },
                {
                    "date": "2025-08-15",
                    "description": "ACH DEBIT PAYPAL *NETFLIX",
                    "amount": "₹799",
                },
            ],
        },
        {
            "name": "Cult.fit",
            "frequency": "monthly",
            "category": "Health",
            "amount": "₹999",
            "date": "2025-09-08",
            "initial": "C",
            "bg": "#E0F2FE",
            "payment_mechanism": "UPI Autopay",
            "cancellation_steps": [
                "Open the Cult.fit app on your mobile device.",
                "Tap the Profile icon in the top right corner and select 'Active Packs / Subscriptions'.",
                "Select your active Cultpass membership.",
                "Tap 'Manage Auto-Renew' and select 'Turn off Auto-Renewal'.",
            ],
            "history": [
                {
                    "date": "2025-05-11",
                    "description": "CULTFIT MEMBERSHIP",
                    "amount": "₹999",
                },
                {
                    "date": "2025-06-10",
                    "description": "CULTFIT MEMBERSHIP",
                    "amount": "₹999",
                },
                {
                    "date": "2025-07-10",
                    "description": "CULTFIT MEMBERSHIP",
                    "amount": "₹999",
                },
                {
                    "date": "2025-08-09",
                    "description": "CULTFIT MEMBERSHIP",
                    "amount": "₹999",
                },
                {
                    "date": "2025-09-08",
                    "description": "CULTFIT MEMBERSHIP",
                    "amount": "₹999",
                },
            ],
        },
        {
            "name": "Amazon Prime",
            "frequency": "annual",
            "category": "Shopping",
            "amount": "₹1,499",
            "date": "2025-05-07",
            "initial": "A",
            "bg": "#DCFCE7",
            "payment_mechanism": "Card recurring",
            "history": [
                {
                    "date": "2025-05-07",
                    "description": "AMZNPRIME ANNUAL",
                    "amount": "₹1,499",
                }
            ],
        },
        {
            "name": "Coursera",
            "frequency": "monthly",
            "category": "Education",
            "amount": "₹499",
            "date": "2025-09-20",
            "initial": "C",
            "bg": "#E0F2FE",
            "history": [
                {
                    "date": "2025-08-20",
                    "description": "COURSERA TRIAL",
                    "amount": "₹0",
                },
                {
                    "date": "2025-09-20",
                    "description": "COURSERA MONTHLY",
                    "amount": "₹499",
                },
            ],
        },
        {
            "name": "OpenAI ChatGPT",
            "frequency": "monthly",
            "category": "Productivity",
            "amount": "₹1,999",
            "date": "2025-09-18",
            "initial": "O",
            "bg": "#E0F2FE",
            "history": [
                {
                    "date": "2025-09-18",
                    "description": "OPENAI CHATGPT",
                    "amount": "₹1,999",
                }
            ],
        },
        {
            "name": "Canva Pro",
            "frequency": "annual",
            "category": "Productivity",
            "amount": "₹3,999",
            "date": "2025-04-12",
            "initial": "C",
            "bg": "#E0F2FE",
            "history": [
                {
                    "date": "2025-03-29",
                    "description": "DRI*CANVA PRO TRIAL",
                    "amount": "₹0",
                },
                {
                    "date": "2025-04-12",
                    "description": "DRI*CANVA ANNUAL",
                    "amount": "₹3,999",
                },
            ],
        },
    ]


# ==========================================
# ICON HELPER FUNCTION
# ==========================================
def load_icon(file_name, size=(24, 24)):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "assets", file_name)

    if os.path.exists(file_path):
        raw_image = Image.open(file_path)
        return CTkImage(light_image=raw_image, dark_image=raw_image, size=size)
    return None


# ==========================================
# 1. SIDEBAR FRAME
# ==========================================
sidebar = CTkFrame(app, width=200, corner_radius=0, fg_color="#FFFFFF")
sidebar.grid(row=0, column=0, sticky="nsew")

logo_img = load_icon("App Logo.jpeg", (160, 100))
logo = CTkLabel(
    sidebar,
    image=logo_img,
    text="The Missing Rupee" if not logo_img else "",
    font=("Arial", 16, "bold"),
    text_color="#343C6A",
)
logo.pack(pady=25, padx=15)

# ==========================================
# 2. CONTENT CONTAINER
# ==========================================
content_area = CTkFrame(app, fg_color="#F8FAFC", corner_radius=0)
content_area.grid(row=0, column=1, sticky="nsew")

content_area.grid_columnconfigure(0, weight=1)
content_area.grid_rowconfigure(0, weight=0)
content_area.grid_rowconfigure(1, weight=1)

# ==========================================
# 2.1 TOP HEADER BAR
# ==========================================
header_frame = CTkFrame(
    content_area, fg_color="#FFFFFF", height=70, corner_radius=0
)
header_frame.grid(row=0, column=0, sticky="ew")

header_title = CTkLabel(
    header_frame,
    text="Overview",
    font=("Arial", 22, "bold"),
    text_color="#343C6A",
)
header_title.pack(side="left", padx=25, pady=20)

header_actions = CTkFrame(header_frame, fg_color="transparent")
header_actions.pack(side="right", padx=25, pady=15)

search_entry = CTkEntry(
    header_actions,
    placeholder_text="Search for something",
    font=("Arial", 12),
    width=220,
    height=40,
    corner_radius=20,
    fg_color="#F5F7FA",
    border_width=0,
    text_color="#232323",
    placeholder_text_color="#8BA3CB",
)
search_entry.pack(side="left", padx=(0, 10))

settings_icon = load_icon("settings.jpg", (20, 20))
settings_btn = CTkButton(
    header_actions,
    text="" if settings_icon else "⚙",
    image=settings_icon,
    width=40,
    height=40,
    corner_radius=20,
    fg_color="#F5F7FA",
    hover_color="#E0E7FF",
    text_color="#718EBF",
)
settings_btn.pack(side="left", padx=(0, 10))

bell_icon = load_icon("bell.png", (20, 20))
notification_btn = CTkButton(
    header_actions,
    text="" if bell_icon else "🔔",
    image=bell_icon,
    width=40,
    height=40,
    corner_radius=20,
    fg_color="#FEF5F5",
    hover_color="#FFE5E5",
    text_color="#FF4D4F",
)
notification_btn.pack(side="left", padx=(0, 10))

profile_img = load_icon("profile.png", (40, 40))
profile_avatar = CTkLabel(
    header_actions,
    text="👤" if not profile_img else "",
    image=profile_img,
    width=40,
    height=40,
    corner_radius=20,
)
profile_avatar.pack(side="left")

# ==========================================
# 3. INDIVIDUAL SCREENS CONTAINER
# ==========================================
screens_container = CTkFrame(content_area, fg_color="transparent")
screens_container.grid(row=1, column=0, sticky="nsew", padx=25, pady=20)
screens_container.grid_columnconfigure(0, weight=1)
screens_container.grid_rowconfigure(0, weight=1)

# --- SCREEN 1: DASHBOARD ---
screen_dashboard = CTkFrame(screens_container, fg_color="transparent")
screen_dashboard.grid(row=0, column=0, sticky="nsew")

# OVERVIEW SECTION
overview_kicker = CTkLabel(
    screen_dashboard,
    text="OVERVIEW",
    font=("Arial", 11, "bold"),
    text_color="#94A3B8",
)
overview_kicker.pack(anchor="w", pady=(0, 2))

overview_heading = CTkLabel(
    screen_dashboard,
    text="Your money, uncovered.",
    font=("Arial", 26, "bold"),
    text_color="#0F172A",
)
overview_heading.pack(anchor="w", pady=(0, 2))

overview_subtitle = CTkLabel(
    screen_dashboard,
    text="A clear view of the recurring payments quietly leaving your account.",
    font=("Arial", 13),
    text_color="#64748B",
)
overview_subtitle.pack(anchor="w", pady=(0, 20))


def create_card(
    parent, icon_symbol, icon_bg, label_text, value_text, footer_text
):
    card = CTkFrame(parent, fg_color="#FFFFFF", corner_radius=16)

    icon_badge = CTkLabel(
        card,
        text=icon_symbol,
        font=("Arial", 16, "bold"),
        fg_color=icon_bg,
        width=36,
        height=36,
        corner_radius=10,
    )
    icon_badge.pack(anchor="w", padx=20, pady=(20, 15))

    lbl = CTkLabel(
        card, text=label_text, font=("Arial", 12), text_color="#64748B"
    )
    lbl.pack(anchor="w", padx=20, pady=(0, 4))

    val = CTkLabel(
        card, text=value_text, font=("Arial", 24, "bold"), text_color="#0F172A"
    )
    val.pack(anchor="w", padx=20, pady=(0, 4))

    foot = CTkLabel(
        card, text=footer_text, font=("Arial", 11), text_color="#94A3B8"
    )
    foot.pack(anchor="w", padx=20, pady=(0, 20))

    return card


def calculate_dashboard_metrics(commitments):
    total_monthly = 0.0
    total_annual = 0.0

    for item in commitments:
        raw_amt = (
            str(item.get("amount", "0")).replace("₹", "").replace(",", "").strip()
        )
        try:
            amt = float(raw_amt)
        except ValueError:
            amt = 0.0

        freq = str(item.get("frequency", "monthly")).lower()

        if freq == "monthly":
            total_monthly += amt
            total_annual += amt * 12
        elif freq == "annual":
            total_monthly += amt / 12.0
            total_annual += amt
        elif freq == "quarterly":
            total_monthly += amt / 3.0
            total_annual += amt * 4
        else:
            total_monthly += amt
            total_annual += amt * 12

    active_count = len(commitments)
    unique_merchants = len({item["name"] for item in commitments})

    return {
        "monthly_str": f"₹{int(round(total_monthly)):,}",
        "annual_str": f"₹{int(round(total_annual)):,}",
        "active_str": str(active_count),
        "merchants_footer": f"From {unique_merchants} merchant pattern{'s' if unique_merchants != 1 else ''}",
    }


metrics = calculate_dashboard_metrics(commitments_data)

cards_frame = CTkFrame(screen_dashboard, fg_color="transparent")
cards_frame.pack(fill="x")

for i in range(3):
    cards_frame.grid_columnconfigure(i, weight=1)

card1 = create_card(
    cards_frame,
    icon_symbol="🔄",
    icon_bg="#E2E8F0",
    label_text="Monthly recurring spend",
    value_text=metrics["monthly_str"],
    footer_text="Across identified commitments",
)
card1.grid(row=0, column=0, padx=(0, 12), sticky="ew")

card2 = create_card(
    cards_frame,
    icon_symbol="🐷",
    icon_bg="#DCFCE7",
    label_text="Annual commitment",
    value_text=metrics["annual_str"],
    footer_text="Your recurring baseline",
)
card2.grid(row=0, column=1, padx=6, sticky="ew")

card3 = create_card(
    cards_frame,
    icon_symbol="✓",
    icon_bg="#E0F2FE",
    label_text="Active subscriptions",
    value_text=metrics["active_str"],
    footer_text=metrics["merchants_footer"],
)
card3.grid(row=0, column=2, padx=(12, 0), sticky="ew")


# ==========================================
# --- SCREEN 2: TRANSACTIONS (List & Details Views) ---
# ==========================================
screen_transactions = CTkFrame(screens_container, fg_color="transparent")
screen_transactions.grid(row=0, column=0, sticky="nsew")

tx_list_container = CTkFrame(screen_transactions, fg_color="transparent")
tx_list_container.pack(fill="both", expand=True)

tx_details_container = CTkScrollableFrame(
    screen_transactions, fg_color="transparent"
)

disc_kicker = CTkLabel(
    tx_list_container,
    text="DISCOVERY",
    font=("Arial", 11, "bold"),
    text_color="#94A3B8",
)
disc_kicker.pack(anchor="w", pady=(0, 2))

top_title_frame = CTkFrame(tx_list_container, fg_color="transparent")
top_title_frame.pack(fill="x", pady=(0, 2))

disc_heading = CTkLabel(
    top_title_frame,
    text="All commitments",
    font=("Arial", 26, "bold"),
    text_color="#0F172A",
)
disc_heading.pack(side="left", anchor="w")

disc_subtitle = CTkLabel(
    tx_list_container,
    text="Every recurring payment we found in your synthetic transaction history.",
    font=("Arial", 13),
    text_color="#64748B",
)
disc_subtitle.pack(anchor="w", pady=(0, 15))

# Filter & Search Control Bar
filter_frame = CTkFrame(tx_list_container, fg_color="transparent")
filter_frame.pack(fill="x", pady=(0, 15))

tx_search_var = StringVar()
category_var = StringVar(value="All categories")
frequency_var = StringVar(value="All frequencies")

tx_search_entry = CTkEntry(
    filter_frame,
    textvariable=tx_search_var,
    placeholder_text="🔍  Search merchant or descriptor",
    font=("Arial", 12),
    height=38,
    corner_radius=8,
    fg_color="#FFFFFF",
    border_width=1,
    border_color="#E2E8F0",
    text_color="#0F172A",
    placeholder_text_color="#94A3B8",
)
tx_search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

category_options = [
    "All categories",
    "Education",
    "Entertainment",
    "Health",
    "Insurance",
    "Productivity",
    "Shopping",
    "Utilities",
]
category_dropdown = CTkOptionMenu(
    filter_frame,
    values=category_options,
    variable=category_var,
    font=("Arial", 12),
    height=38,
    corner_radius=8,
    fg_color="#FFFFFF",
    text_color="#334155",
    button_color="#FFFFFF",
    button_hover_color="#F1F5F9",
    dropdown_fg_color="#FFFFFF",
    dropdown_text_color="#0F172A",
)
category_dropdown.pack(side="left", padx=(0, 10))

frequency_options = ["All frequencies", "annual", "monthly", "quarterly"]
frequency_dropdown = CTkOptionMenu(
    filter_frame,
    values=frequency_options,
    variable=frequency_var,
    font=("Arial", 12),
    height=38,
    corner_radius=8,
    fg_color="#FFFFFF",
    text_color="#334155",
    button_color="#FFFFFF",
    button_hover_color="#F1F5F9",
    dropdown_fg_color="#FFFFFF",
    dropdown_text_color="#0F172A",
)
frequency_dropdown.pack(side="left", padx=(0, 15))

count_label = CTkLabel(
    filter_frame,
    text="13 found",
    font=("Arial", 12),
    text_color="#64748B",
)
count_label.pack(side="left")

# Table Headers
headers_frame = CTkFrame(tx_list_container, fg_color="transparent")
headers_frame.pack(fill="x", padx=15, pady=(0, 8))

headers_frame.grid_columnconfigure(0, weight=4)
headers_frame.grid_columnconfigure(1, weight=3)
headers_frame.grid_columnconfigure(2, weight=3)
headers_frame.grid_columnconfigure(3, weight=2)

CTkLabel(
    headers_frame,
    text="MERCHANT",
    font=("Arial", 11, "bold"),
    text_color="#94A3B8",
).grid(row=0, column=0, sticky="w")
CTkLabel(
    headers_frame,
    text="AMOUNT / FREQUENCY",
    font=("Arial", 11, "bold"),
    text_color="#94A3B8",
).grid(row=0, column=1, sticky="w")
CTkLabel(
    headers_frame,
    text="LAST PAYMENT",
    font=("Arial", 11, "bold"),
    text_color="#94A3B8",
).grid(row=0, column=2, sticky="w")
CTkLabel(
    headers_frame,
    text="CONFIDENCE",
    font=("Arial", 11, "bold"),
    text_color="#94A3B8",
).grid(row=0, column=3, sticky="e")

commitments_scroll = CTkScrollableFrame(
    tx_list_container,
    fg_color="transparent",
    corner_radius=0,
)
commitments_scroll.pack(fill="both", expand=True)


def bind_click_recursive(widget, callback):
    widget.bind("<Button-1>", callback)
    for child in widget.winfo_children():
        bind_click_recursive(child, callback)


def show_list_view():
    tx_details_container.pack_forget()
    tx_list_container.pack(fill="both", expand=True)


def open_commitment_details(item):
    tx_list_container.pack_forget()
    tx_details_container.pack(fill="both", expand=True)

    for child in tx_details_container.winfo_children():
        child.destroy()

    # Back Link
    back_btn = CTkButton(
        tx_details_container,
        text="←  All commitments",
        font=("Arial", 12, "bold"),
        text_color="#0D9488",
        fg_color="transparent",
        hover_color="#F1F5F9",
        anchor="w",
        height=28,
        command=show_list_view,
    )
    back_btn.pack(anchor="w", pady=(0, 10))

    # Investigation Header
    CTkLabel(
        tx_details_container,
        text="INVESTIGATION",
        font=("Arial", 11, "bold"),
        text_color="#94A3B8",
    ).pack(anchor="w", pady=(0, 2))

    CTkLabel(
        tx_details_container,
        text=item["name"],
        font=("Arial", 28, "bold"),
        text_color="#0F172A",
    ).pack(anchor="w", pady=(0, 2))

    descriptor = item["name"].upper().replace(" ", "")
    CTkLabel(
        tx_details_container,
        text=f"{descriptor} · evidence-based recurring payment review",
        font=("Arial", 12),
        text_color="#64748B",
    ).pack(anchor="w", pady=(0, 18))

    # Hero Summary Card
    hero_card = CTkFrame(
        tx_details_container,
        fg_color="#FFFFFF",
        corner_radius=12,
        border_width=1,
        border_color="#F1F5F9",
    )
    hero_card.pack(fill="x", pady=(0, 16))

    hero_left = CTkFrame(hero_card, fg_color="transparent")
    hero_left.pack(side="left", padx=20, pady=20)

    badge = CTkLabel(
        hero_left,
        text=item["initial"],
        font=("Arial", 20, "bold"),
        fg_color=item["bg"],
        text_color="#1E293B",
        width=52,
        height=52,
        corner_radius=12,
    )
    badge.pack(side="left", padx=(0, 16))

    hero_info = CTkFrame(hero_left, fg_color="transparent")
    hero_info.pack(side="left")

    amt_freq_frame = CTkFrame(hero_info, fg_color="transparent")
    amt_freq_frame.pack(anchor="w")

    CTkLabel(
        amt_freq_frame,
        text=item["amount"],
        font=("Arial", 22, "bold"),
        text_color="#0F172A",
    ).pack(side="left")
    CTkLabel(
        amt_freq_frame,
        text=f" /{item['frequency']}",
        font=("Arial", 13),
        text_color="#64748B",
    ).pack(side="left", padx=(2, 0))

    CTkLabel(
        hero_info,
        text=f"Estimated next payment: {item['date']}",
        font=("Arial", 11),
        text_color="#64748B",
    ).pack(anchor="w", pady=(2, 6))

    conf_badge = CTkLabel(
        hero_info,
        text="HIGH CONFIDENCE",
        font=("Arial", 9, "bold"),
        fg_color="#DCFCE7",
        text_color="#166534",
        corner_radius=6,
        padx=8,
        pady=2,
    )
    conf_badge.pack(anchor="w")

    hero_right = CTkFrame(hero_card, fg_color="transparent")
    hero_right.pack(side="right", padx=25, pady=20)

    raw_amt = float(
        item["amount"].replace("₹", "").replace(",", "").strip() or 0
    )
    freq_str = item["frequency"].lower()
    annual_cost = (
        raw_amt
        if freq_str == "annual"
        else (raw_amt * 4 if freq_str == "quarterly" else raw_amt * 12)
    )

    CTkLabel(
        hero_right,
        text="Annual cost",
        font=("Arial", 11),
        text_color="#94A3B8",
        anchor="e",
    ).pack(anchor="e")
    CTkLabel(
        hero_right,
        text=f"₹{int(round(annual_cost)):,}",
        font=("Arial", 20, "bold"),
        text_color="#0F172A",
        anchor="e",
    ).pack(anchor="e")

    # Payment History Section
    history_list = item.get("history", [])

    if not history_list:
        try:
            search_keyword = item["name"].split()[0]
            cursor.execute(
                """
                SELECT transaction_date::text, description, amount::float
                FROM transactions
                WHERE description ILIKE %s AND transaction_type = 'debit'
                ORDER BY transaction_date ASC;
                """,
                (f"%{search_keyword}%",),
            )
            rows = cursor.fetchall()
            if rows:
                history_list = [
                    {
                        "date": r[0][:10],
                        "description": r[1],
                        "amount": f"₹{int(r[2]):,}"
                        if float(r[2]).is_integer()
                        else f"₹{r[2]:,.2f}",
                    }
                    for r in rows
                ]
        except Exception as e:
            print("History query error:", e)

    if not history_list:
        history_list = [
            {
                "date": item["date"],
                "description": item["name"].upper(),
                "amount": item["amount"],
            }
        ]

    history_card = CTkFrame(
        tx_details_container,
        fg_color="#FFFFFF",
        corner_radius=12,
        border_width=1,
        border_color="#F1F5F9",
    )
    history_card.pack(fill="x", pady=(0, 16), padx=1)

    CTkLabel(
        history_card,
        text="Payment history",
        font=("Arial", 15, "bold"),
        text_color="#0F172A",
    ).pack(anchor="w", padx=20, pady=(15, 2))

    count_txt = (
        f"Matched {len(history_list)} payment{'s' if len(history_list) != 1 else ''} "
        f"for {item['name']} with a {item['frequency']} billing pattern. "
        f"Amounts are compared within the same merchant and payment mechanism."
    )
    CTkLabel(
        history_card,
        text=count_txt,
        font=("Arial", 12),
        text_color="#64748B",
        wraplength=700,
        justify="left",
    ).pack(anchor="w", padx=20, pady=(0, 15))

    for idx, hist in enumerate(history_list):
        is_latest = idx == (len(history_list) - 1)

        hist_row = CTkFrame(history_card, fg_color="transparent")
        hist_row.pack(fill="x", padx=20, pady=6)

        hist_left = CTkFrame(hist_row, fg_color="transparent")
        hist_left.pack(side="left")

        CTkLabel(
            hist_left,
            text="•",
            font=("Arial", 16, "bold"),
            text_color="#10B981",
        ).pack(side="left", padx=(0, 10))

        CTkLabel(
            hist_left,
            text=hist["date"],
            font=("Arial", 12, "bold"),
            text_color="#334155",
        ).pack(side="left", padx=(0, 20))

        CTkLabel(
            hist_left,
            text=hist.get("description", item["name"].upper()),
            font=("Arial", 11),
            text_color="#64748B",
        ).pack(side="left")

        hist_right = CTkFrame(hist_row, fg_color="transparent")
        hist_right.pack(side="right")

        CTkLabel(
            hist_right,
            text=hist["amount"],
            font=("Arial", 13, "bold"),
            text_color="#0F172A",
        ).pack(side="left", padx=(0, 8))

        if is_latest:
            CTkLabel(
                hist_right,
                text="Latest",
                font=("Arial", 10, "bold"),
                fg_color="#DCFCE7",
                text_color="#166534",
                corner_radius=6,
                padx=6,
                pady=1,
            ).pack(side="left")

        if not is_latest:
            sep = CTkFrame(history_card, fg_color="#F8FAFC", height=1)
            sep.pack(fill="x", padx=20, pady=(2, 2))

    CTkFrame(history_card, fg_color="transparent", height=10).pack()

    # Guided Cancellation Card
    cancel_card = CTkFrame(
        tx_details_container,
        fg_color="#FFFFFF",
        corner_radius=12,
        border_width=1,
        border_color="#F1F5F9",
    )
    cancel_card.pack(fill="x", pady=(0, 20), ipadx=10, ipady=10)

    CTkLabel(
        cancel_card,
        text="GUIDED CANCELLATION",
        font=("Arial", 11, "bold"),
        text_color="#94A3B8",
    ).pack(anchor="w", padx=20, pady=(15, 2))

    CTkLabel(
        cancel_card,
        text="How to stop this payment",
        font=("Arial", 16, "bold"),
        text_color="#0F172A",
    ).pack(anchor="w", padx=20, pady=(0, 10))

    pay_mech = item.get("payment_mechanism", "Card recurring")
    mech_pill = CTkLabel(
        cancel_card,
        text=f"  ✓  Payment mechanism: {pay_mech}  ",
        font=("Arial", 11, "bold"),
        fg_color="#F1F5F9",
        text_color="#334155",
        corner_radius=8,
        height=32,
    )
    mech_pill.pack(anchor="w", padx=20, pady=(0, 15))

    default_steps = [
        f"Log into your {item['name']} account on their official website or app.",
        "Navigate to Account Settings or Subscription & Billing.",
        "Select your active plan and click 'Cancel Subscription' or 'Disable Auto-Renew'.",
        "Save the cancellation confirmation receipt for your records.",
    ]

    steps = item.get("cancellation_steps", default_steps)

    for idx, step_text in enumerate(steps, start=1):
        step_row = CTkFrame(cancel_card, fg_color="transparent")
        step_row.pack(fill="x", padx=20, pady=5)

        CTkLabel(
            step_row,
            text=str(idx),
            font=("Arial", 11, "bold"),
            fg_color="#0F172A",
            text_color="#FFFFFF",
            width=22,
            height=22,
            corner_radius=11,
        ).pack(side="left", padx=(0, 12), anchor="n")

        CTkLabel(
            step_row,
            text=step_text,
            font=("Arial", 12),
            text_color="#334155",
            anchor="w",
            wraplength=650,
            justify="left",
        ).pack(side="left", fill="x", expand=True)

    warning_box = CTkFrame(
        cancel_card,
        fg_color="#FEF3C7",
        corner_radius=8,
        border_width=1,
        border_color="#FDE68A",
    )
    warning_box.pack(fill="x", padx=20, pady=(18, 15))

    warn_inner = CTkFrame(warning_box, fg_color="transparent")
    warn_inner.pack(fill="x", padx=12, pady=10)

    CTkLabel(warn_inner, text="⚠️", font=("Arial", 14)).pack(
        side="left", anchor="n", padx=(0, 8)
    )

    warn_text = (
        "Important distinction: Revoking a mandate may stop future debits "
        "but does not automatically terminate the underlying merchant contract."
    )
    CTkLabel(
        warn_inner,
        text=warn_text,
        font=("Arial", 11, "bold"),
        text_color="#92400E",
        wraplength=650,
        justify="left",
    ).pack(side="left", fill="x", expand=True)


def render_commitments(items):
    for widget in commitments_scroll.winfo_children():
        widget.destroy()

    count_label.configure(text=f"{len(items)} found")

    for item in items:
        row_card = CTkFrame(
            commitments_scroll, fg_color="#FFFFFF", corner_radius=10, height=58
        )
        row_card.pack(fill="x", pady=4, padx=2)
        row_card.pack_propagate(False)

        left_box = CTkFrame(row_card, fg_color="transparent")
        left_box.pack(side="left", padx=12)

        badge = CTkLabel(
            left_box,
            text=item["initial"],
            font=("Arial", 14, "bold"),
            fg_color=item["bg"],
            text_color="#1E293B",
            width=36,
            height=36,
            corner_radius=8,
        )
        badge.pack(side="left", padx=(0, 12))

        text_box = CTkFrame(left_box, fg_color="transparent")
        text_box.pack(side="left")

        name_lbl = CTkLabel(
            text_box,
            text=item["name"],
            font=("Arial", 13, "bold"),
            text_color="#0F172A",
            anchor="w",
        )
        name_lbl.pack(anchor="w")

        sub_lbl = CTkLabel(
            text_box,
            text=f"{item['frequency']} · {item['category']}",
            font=("Arial", 11),
            text_color="#64748B",
            anchor="w",
        )
        sub_lbl.pack(anchor="w")

        right_box = CTkFrame(row_card, fg_color="transparent")
        right_box.pack(side="right", padx=15)

        val_box = CTkFrame(right_box, fg_color="transparent")
        val_box.pack(side="left", padx=(0, 15))

        amt_lbl = CTkLabel(
            val_box,
            text=item["amount"],
            font=("Arial", 13, "bold"),
            text_color="#0F172A",
            anchor="e",
        )
        amt_lbl.pack(anchor="e")

        dt_lbl = CTkLabel(
            val_box,
            text=item["date"],
            font=("Arial", 11),
            text_color="#64748B",
            anchor="e",
        )
        dt_lbl.pack(anchor="e")

        chevron = CTkLabel(
            right_box,
            text="›",
            font=("Arial", 18),
            text_color="#94A3B8",
        )
        chevron.pack(side="right")

        bind_click_recursive(
            row_card, lambda e, it=item: open_commitment_details(it)
        )


def filter_commitments(*args):
    q = tx_search_var.get().lower().strip()
    cat = category_var.get()
    freq = frequency_var.get()

    filtered = []
    for item in commitments_data:
        matches_q = (
            not q
            or (q in item["name"].lower())
            or (q in item["category"].lower())
            or (q in item["frequency"].lower())
        )
        matches_cat = (cat == "All categories") or (item["category"] == cat)
        matches_freq = (freq == "All frequencies") or (item["frequency"] == freq)

        if matches_q and matches_cat and matches_freq:
            filtered.append(item)

    render_commitments(filtered)


tx_search_var.trace_add("write", filter_commitments)
category_dropdown.configure(command=lambda _: filter_commitments())
frequency_dropdown.configure(command=lambda _: filter_commitments())

render_commitments(commitments_data)


# ==========================================
# --- SCREEN 3: ALERTS & INSIGHTS ---
# ==========================================
screen_alerts = CTkFrame(screens_container, fg_color="transparent")
screen_alerts.grid(row=0, column=0, sticky="nsew")

# Header section
CTkLabel(
    screen_alerts,
    text="SIGNALS",
    font=("Arial", 11, "bold"),
    text_color="#94A3B8",
).pack(anchor="w", pady=(0, 2))

CTkLabel(
    screen_alerts,
    text="Alerts & insights",
    font=("Arial", 26, "bold"),
    text_color="#0F172A",
).pack(anchor="w", pady=(0, 2))

CTkLabel(
    screen_alerts,
    text="Understand what changed before it quietly costs you more.",
    font=("Arial", 13),
    text_color="#64748B",
).pack(anchor="w", pady=(0, 15))

alerts_scroll = CTkScrollableFrame(
    screen_alerts, fg_color="transparent", corner_radius=0
)
alerts_scroll.pack(fill="both", expand=True)


def parse_amount_value(amt_str):
    raw = str(amt_str).replace("₹", "").replace(",", "").strip()
    try:
        return float(raw)
    except ValueError:
        return 0.0


def calculate_dynamic_alerts(commitments):
    """Calculates alerts based on price hikes, frequency increases, or trial/new subscriptions."""
    alerts = []

    for item in commitments:
        name = item.get("name", "Merchant")
        history = item.get("history", [])

        # 1. Price Hike & Free Trial Conversion check across history
        if len(history) >= 2:
            for i in range(1, len(history)):
                prev_amt = parse_amount_value(history[i - 1].get("amount", "0"))
                curr_amt = parse_amount_value(history[i].get("amount", "0"))

                # Price Hike
                if prev_amt > 0 and curr_amt > prev_amt:
                    pct = int(round(((curr_amt - prev_amt) / prev_amt) * 100))
                    alerts.append(
                        {
                            "title": f"{name} price increased",
                            "subtitle": f"Your recurring charge changed from {history[i-1]['amount']} to {history[i]['amount']}.",
                            "merchant": name,
                            "date": history[i]["date"],
                            "change": f"{history[i-1]['amount']} → {history[i]['amount']} (+{pct}%)",
                            "item": item,
                        }
                    )
                # Free Trial Conversion
                elif prev_amt == 0 and curr_amt > 0:
                    alerts.append(
                        {
                            "title": f"Free trial converted",
                            "subtitle": f"A free trial for {name} was followed by a {history[i]['amount']} recurring subscription charge.",
                            "merchant": name,
                            "date": history[i]["date"],
                            "change": f"₹0 → {history[i]['amount']}",
                            "item": item,
                        }
                    )

        # 2. Newly Started Subscription Check
        elif len(history) == 1:
            alerts.append(
                {
                    "title": f"New recurring payment started",
                    "subtitle": f"A new recurring commitment of {item['amount']} was detected for {name}.",
                    "merchant": name,
                    "date": item["date"],
                    "change": f"New ({item['amount']})",
                    "item": item,
                }
            )

        # 3. Frequency Increase Check
        if item.get("frequency_increased", False):
            alerts.append(
                {
                    "title": f"Billing frequency increased",
                    "subtitle": f"Payment schedule for {name} increased in frequency to {item['frequency']}.",
                    "merchant": name,
                    "date": item["date"],
                    "change": f"Frequency: {item['frequency']}",
                    "item": item,
                }
            )

    # Sort alerts by date descending
    alerts.sort(key=lambda x: x["date"], reverse=True)
    return alerts


def format_date_label(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%d %b %Y")
    except Exception:
        return date_str


def render_alerts_feed():
    for child in alerts_scroll.winfo_children():
        child.destroy()

    alerts_data = calculate_dynamic_alerts(commitments_data)

    if not alerts_data:
        empty_lbl = CTkLabel(
            alerts_scroll,
            text="No alerts detected in your transaction history.",
            font=("Arial", 14),
            text_color="#64748B",
        )
        empty_lbl.pack(pady=40)
        return

    # Group alerts by date
    grouped = {}
    for alert in alerts_data:
        d = alert["date"]
        if d not in grouped:
            grouped[d] = []
        grouped[d].append(alert)

    # Render each date group with a date separator
    for d_str in sorted(grouped.keys(), reverse=True):
        # --- DATE-WISE SEPARATOR ---
        sep_frame = CTkFrame(alerts_scroll, fg_color="transparent")
        sep_frame.pack(fill="x", pady=(12, 8))

        line_left = CTkFrame(sep_frame, fg_color="#E2E8F0", height=1)
        line_left.pack(side="left", fill="x", expand=True, padx=(0, 10))

        date_lbl = CTkLabel(
            sep_frame,
            text=f"───  {format_date_label(d_str)}  ───",
            font=("Arial", 11, "bold"),
            text_color="#64748B",
        )
        date_lbl.pack(side="left")

        line_right = CTkFrame(sep_frame, fg_color="#E2E8F0", height=1)
        line_right.pack(side="right", fill="x", expand=True, padx=(10, 0))

        # --- ALERT CARDS FOR THIS DATE ---
        for alert in grouped[d_str]:
            card = CTkFrame(
                alerts_scroll,
                fg_color="#FFFFFF",
                corner_radius=12,
                border_width=1,
                border_color="#F1F5F9",
            )
            card.pack(fill="x", pady=5, padx=2)

            # Left side (Icon + Text)
            left_frame = CTkFrame(card, fg_color="transparent")
            left_frame.pack(side="left", padx=15, pady=15)

            icon_badge = CTkLabel(
                left_frame,
                text="⚠️",
                font=("Arial", 14),
                fg_color="#FEF2F2",
                width=36,
                height=36,
                corner_radius=18,
            )
            icon_badge.pack(side="left", padx=(0, 12))

            text_box = CTkFrame(left_frame, fg_color="transparent")
            text_box.pack(side="left")

            title_lbl = CTkLabel(
                text_box,
                text=alert["title"],
                font=("Arial", 13, "bold"),
                text_color="#0F172A",
                anchor="w",
            )
            title_lbl.pack(anchor="w")

            sub_lbl = CTkLabel(
                text_box,
                text=alert["subtitle"],
                font=("Arial", 11),
                text_color="#64748B",
                anchor="w",
                wraplength=450,
                justify="left",
            )
            sub_lbl.pack(anchor="w")

            # Right side metadata + Investigate button
            right_frame = CTkFrame(card, fg_color="transparent")
            right_frame.pack(side="right", padx=15, pady=15)

            meta_lbl = CTkLabel(
                right_frame,
                text=f"Merchant: {alert['merchant']}   Observed: {alert['date']}   Change: {alert['change']}",
                font=("Arial", 11),
                text_color="#64748B",
            )
            meta_lbl.pack(side="left", padx=(0, 15))

            investigate_btn = CTkButton(
                right_frame,
                text="Investigate ↗",
                font=("Arial", 12, "bold"),
                text_color="#0D9488",
                fg_color="transparent",
                hover_color="#F1F5F9",
                width=100,
                height=32,
                command=lambda item=alert["item"]: navigate_to_investigation(item),
            )
            investigate_btn.pack(side="right")


def navigate_to_investigation(target_item):
    """Switch tab to Transactions and open details for the selected merchant."""
    select_menu("Transactions")
    open_commitment_details(target_item)


# Initial render of alerts
render_alerts_feed()


# ==========================================
# 4. TAB NAVIGATION CONTROLLER
# ==========================================
screens = {
    "Dashboard": screen_dashboard,
    "Transactions": screen_transactions,
    "Alerts & Insights": screen_alerts,
}

menu_buttons = {}


def select_menu(selected_name):
    screens[selected_name].tkraise()
    header_title.configure(
        text="Overview" if selected_name == "Dashboard" else selected_name
    )

    for name, btn in menu_buttons.items():
        if name == selected_name:
            btn.configure(fg_color="#1814F3", text_color="#FFFFFF")
        else:
            btn.configure(fg_color="transparent", text_color="#718EBF")


menu_options = ["Dashboard", "Transactions", "Alerts & Insights"]

for name in menu_options:
    btn = CTkButton(
        sidebar,
        text=name,
        font=("Arial", 14, "bold"),
        corner_radius=12,
        fg_color="transparent",
        text_color="#718EBF",
        hover_color="#E0E7FF",
        anchor="w",
        height=42,
        command=lambda n=name: select_menu(n),
    )
    btn.pack(fill="x", padx=15, pady=6)
    menu_buttons[name] = btn

# Set default tab
select_menu("Dashboard")

app.mainloop()
connection.close()