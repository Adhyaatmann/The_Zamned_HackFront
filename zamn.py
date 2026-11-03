from datetime import datetime
import os
import psycopg2
from dotenv import load_dotenv
from customtkinter import *
from PIL import Image, ImageDraw

# Matplotlib & Tkinter Integration
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter
import numpy as np
from gemini_analyzer import get_commitments_from_gemini

# ==========================================
# LOAD ENVIRONMENT & DATABASE
# ==========================================
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
try:
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()
except Exception as e:
    print(f"⚠️ Database connection warning: {e}")
    connection, cursor = None, None

app = CTk()
app.geometry("1150x780")
app.title("The Missing Rupee - Financial Discovery & Anti-Dark Patterns")

# Configure main window grid
app.grid_columnconfigure(1, weight=1)
app.grid_rowconfigure(0, weight=1)

# Global variables for settings states
current_theme_var = StringVar(value="Light")
current_scale_var = StringVar(value="100%")
settings_window = None

# Set initial appearance mode
set_appearance_mode("Light")

# ==========================================
# FETCH COMMITMENTS DATA
# ==========================================
try:
    print("DEBUG: Fetching live data from Supabase & Gemini...")
    commitments_data = get_commitments_from_gemini()
    print(f"DEBUG: App received {len(commitments_data)} commitments.")
except Exception as e:
    print(f"❌ DEBUG: Exception during startup fetch: {e}")
    commitments_data = []

# Fallback sample data if DB or Gemini call fails
if not commitments_data:
    print("⚠️ DEBUG: Using fallback commitments_data.")
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
                "Under the 'Membership & Billing' section, click 'Cancel Membership'.",
                "Click 'Finish Cancellation' to stop future automatic debits.",
            ],
            "history": [
                {"date": "2025-03-15", "description": "ACH DEBIT PAYPAL *NETFLIX", "amount": "₹649"},
                {"date": "2025-04-15", "description": "ACH DEBIT PAYPAL *NETFLIX", "amount": "₹649"},
                {"date": "2025-05-15", "description": "ACH DEBIT PAYPAL *NETFLIX", "amount": "₹649"},
                {"date": "2025-06-15", "description": "ACH DEBIT PAYPAL *NETFLIX", "amount": "₹649"},
                {"date": "2025-07-15", "description": "ACH DEBIT PAYPAL *NETFLIX", "amount": "₹799"},
                {"date": "2025-08-15", "description": "ACH DEBIT PAYPAL *NETFLIX", "amount": "₹799"},
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
                {"date": "2025-05-11", "description": "CULTFIT MEMBERSHIP", "amount": "₹999"},
                {"date": "2025-06-10", "description": "CULTFIT MEMBERSHIP", "amount": "₹999"},
                {"date": "2025-07-10", "description": "CULTFIT MEMBERSHIP", "amount": "₹999"},
                {"date": "2025-08-09", "description": "CULTFIT MEMBERSHIP", "amount": "₹999"},
                {"date": "2025-09-08", "description": "CULTFIT MEMBERSHIP", "amount": "₹999"},
            ],
        },
        {"name": "Amazon Prime", "frequency": "annual", "category": "Shopping", "amount": "₹1,499", "date": "2025-05-07", "initial": "A", "bg": "#DCFCE7"},
        {"name": "Coursera", "frequency": "monthly", "category": "Education", "amount": "₹499", "date": "2025-09-20", "initial": "C", "bg": "#E0F2FE"},
        {"name": "OpenAI ChatGPT", "frequency": "monthly", "category": "Productivity", "amount": "₹1,999", "date": "2025-09-18", "initial": "O", "bg": "#E0F2FE"},
        {"name": "Canva Pro", "frequency": "annual", "category": "Productivity", "amount": "₹3,999", "date": "2025-04-12", "initial": "C", "bg": "#E0F2FE"},
        {"name": "LIC Premium", "frequency": "quarterly", "category": "Insurance", "amount": "₹2,200", "date": "2025-11-17", "initial": "L", "bg": "#DCFCE7"},
        {"name": "Apple iCloud", "frequency": "monthly", "category": "Utilities", "amount": "₹75", "date": "2025-09-05", "initial": "A", "bg": "#F1F5F9"},
    ]


# ==========================================
# IMAGE ROUNDING & DUAL ICON HELPER
# ==========================================
def make_rounded_image(image, radius=14):
    if image is None:
        return None
    image = image.convert("RGBA")
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), image.size], radius=radius, fill=255)
    rounded = Image.new("RGBA", image.size, (0, 0, 0, 0))
    rounded.paste(image, (0, 0), mask=mask)
    return rounded


def load_icon(file_name, size=(24, 24), corner_radius=0):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    light_path = os.path.join(base_dir, "assets", file_name)

    # Fallback between .png and .jpeg if needed
    if not os.path.exists(light_path):
        name_part, ext = os.path.splitext(file_name)
        alt_ext = ".jpeg" if ext.lower() == ".png" else ".png"
        alt_path = os.path.join(base_dir, "assets", name_part + alt_ext)
        if os.path.exists(alt_path):
            light_path = alt_path

    name_part, ext = os.path.splitext(os.path.basename(light_path))
    dark_file = f"{name_part}_dark{ext}"
    dark_path = os.path.join(base_dir, "assets", dark_file)

    light_img = Image.open(light_path) if os.path.exists(light_path) else None
    dark_img = Image.open(dark_path) if os.path.exists(dark_path) else light_img

    if light_img:
        if corner_radius > 0:
            light_img = make_rounded_image(light_img, corner_radius)
            if dark_img and dark_img != light_img:
                dark_img = make_rounded_image(dark_img, corner_radius)
            else:
                dark_img = light_img

        return CTkImage(light_image=light_img, dark_image=dark_img, size=size)
    return None


# ==========================================
# SETTINGS MODAL & EVENT DEFERRAL
# ==========================================
def refresh_all_charts():
    if 'trend_range_var' in globals():
        update_trend_chart(trend_range_var.get())
    if 'render_category_chart' in globals():
        render_category_chart()


def change_appearance_theme(choice):
    set_appearance_mode(choice)
    
    if settings_window is not None and settings_window.winfo_exists():
        settings_window.deiconify()
        settings_window.lift()
        settings_window.focus_force()

    app.after(100, refresh_all_charts)


def change_widget_scaling(choice):
    scale_map = {"80%": 0.8, "90%": 0.9, "100%": 1.0, "110%": 1.1, "120%": 1.2}
    scale_val = scale_map.get(choice, 1.0)
    
    set_widget_scaling(scale_val)

    if settings_window is not None and settings_window.winfo_exists():
        settings_window.deiconify()
        settings_window.lift()
        settings_window.focus_force()

    app.after(100, refresh_all_charts)


def open_settings_modal():
    global settings_window

    if settings_window is not None and settings_window.winfo_exists():
        settings_window.deiconify()
        settings_window.lift()
        settings_window.focus_force()
        return

    settings_window = CTkToplevel(app, fg_color=("#F8FAFC", "#0F172A"))
    settings_window.title("Preferences & Settings")
    settings_window.geometry("440x450")
    settings_window.minsize(400, 380)

    settings_window.transient(app)
    settings_window.lift()
    settings_window.focus_force()

    def on_close_settings():
        global settings_window
        if settings_window is not None:
            settings_window.destroy()
            settings_window = None

    settings_window.protocol("WM_DELETE_WINDOW", on_close_settings)

    # Scrollable wrapper container with valid theme color tuple
    modal_scroll = CTkScrollableFrame(settings_window, fg_color=("#F8FAFC", "#0F172A"))
    modal_scroll.pack(fill="both", expand=True, padx=10, pady=10)

    # Title Banner with loaded settings icon
    header = CTkFrame(modal_scroll, fg_color="transparent")
    header.pack(fill="x", padx=10, pady=(10, 15))

    title_box = CTkFrame(header, fg_color="transparent")
    title_box.pack(anchor="w")

    set_img = load_icon("settings.png", (22, 22))
    if set_img:
        icon_lbl = CTkLabel(title_box, text="", image=set_img)
        icon_lbl.pack(side="left", padx=(0, 8))

    CTkLabel(title_box, text="Preferences", font=("Arial", 20, "bold"), text_color=("#0F172A", "#F8FAFC")).pack(side="left")
    CTkLabel(header, text="Customize your app theme and text scaling.", font=("Arial", 12), text_color=("#64748B", "#94A3B8")).pack(anchor="w", pady=(2, 0))

    # Container Card
    container = CTkFrame(modal_scroll, fg_color=("#FFFFFF", "#1E293B"), corner_radius=12)
    container.pack(fill="both", expand=True, padx=5, pady=(0, 10))

    # --- SETTING 1: THEME SELECTOR ---
    theme_frame = CTkFrame(container, fg_color="transparent")
    theme_frame.pack(fill="x", padx=20, pady=(20, 15))

    CTkLabel(theme_frame, text="Appearance Theme", font=("Arial", 13, "bold"), text_color=("#0F172A", "#F8FAFC")).pack(anchor="w", pady=(0, 2))
    CTkLabel(theme_frame, text="Choose between light, dark, or system mode.", font=("Arial", 11), text_color=("#64748B", "#94A3B8")).pack(anchor="w", pady=(0, 8))

    theme_segmented = CTkSegmentedButton(
        theme_frame,
        values=["Light", "Dark", "System"],
        variable=current_theme_var,
        command=change_appearance_theme,
        font=("Arial", 12, "bold"),
        height=32,
    )
    theme_segmented.pack(fill="x")

    # Divider
    CTkFrame(container, fg_color=("#E2E8F0", "#334155"), height=1).pack(fill="x", padx=20, pady=5)

    # --- SETTING 2: FONT & UI SCALING ---
    scale_frame = CTkFrame(container, fg_color="transparent")
    scale_frame.pack(fill="x", padx=20, pady=(15, 20))

    CTkLabel(scale_frame, text="Font & UI Scaling", font=("Arial", 13, "bold"), text_color=("#0F172A", "#F8FAFC")).pack(anchor="w", pady=(0, 2))
    CTkLabel(scale_frame, text="Adjust widget padding and typography size.", font=("Arial", 11), text_color=("#64748B", "#94A3B8")).pack(anchor="w", pady=(0, 8))

    scale_segmented = CTkSegmentedButton(
        scale_frame,
        values=["80%", "90%", "100%", "110%", "120%"],
        variable=current_scale_var,
        command=change_widget_scaling,
        font=("Arial", 12, "bold"),
        height=32,
    )
    scale_segmented.pack(fill="x")


# ==========================================
# 1. SIDEBAR FRAME
# ==========================================
sidebar = CTkFrame(app, width=200, corner_radius=0, fg_color=("#FFFFFF", "#1E293B"))
sidebar.grid(row=0, column=0, sticky="nsew")

logo_img = load_icon("App Logo.png", (160, 100), corner_radius=14)
logo = CTkLabel(
    sidebar,
    image=logo_img,
    text="The Missing Rupee" if not logo_img else "",
    font=("Arial", 16, "bold"),
    text_color=("#343C6A", "#F8FAFC"),
)
logo.pack(pady=25, padx=15)

# ==========================================
# 2. CONTENT CONTAINER
# ==========================================
content_area = CTkFrame(app, fg_color=("#F8FAFC", "#0F172A"), corner_radius=0)
content_area.grid(row=0, column=1, sticky="nsew")

content_area.grid_columnconfigure(0, weight=1)
content_area.grid_rowconfigure(0, weight=0)
content_area.grid_rowconfigure(1, weight=1)

# ==========================================
# 2.1 TOP HEADER BAR
# ==========================================
header_frame = CTkFrame(content_area, fg_color=("#FFFFFF", "#1E293B"), height=70, corner_radius=0)
header_frame.grid(row=0, column=0, sticky="ew")

header_title = CTkLabel(
    header_frame,
    text="Overview",
    font=("Arial", 22, "bold"),
    text_color=("#343C6A", "#F8FAFC"),
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
    fg_color=("#F5F7FA", "#334155"),
    border_width=0,
    text_color=("#232323", "#F8FAFC"),
    placeholder_text_color=("#8BA3CB", "#94A3B8"),
)
search_entry.pack(side="left", padx=(0, 10))

settings_icon = load_icon("settings.png", (20, 20))
settings_btn = CTkButton(
    header_actions,
    text="" if settings_icon else "⚙",
    image=settings_icon,
    width=40,
    height=40,
    corner_radius=20,
    fg_color=("#F5F7FA", "#334155"),
    hover_color=("#E0E7FF", "#475569"),
    text_color=("#718EBF", "#F8FAFC"),
    command=open_settings_modal,
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
    fg_color=("#FEF5F5", "#334155"),
    hover_color=("#FFE5E5", "#475569"),
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
# 3. SCREENS CONTAINER
# ==========================================
screens_container = CTkFrame(content_area, fg_color="transparent")
screens_container.grid(row=1, column=0, sticky="nsew", padx=25, pady=20)
screens_container.grid_columnconfigure(0, weight=1)
screens_container.grid_rowconfigure(0, weight=1)

# --- SCREEN 1: DASHBOARD ---
screen_dashboard = CTkScrollableFrame(screens_container, fg_color=("#F8FAFC", "#0F172A"))

CTkLabel(screen_dashboard, text="OVERVIEW", font=("Arial", 11, "bold"), text_color=("#94A3B8", "#64748B")).pack(anchor="w", pady=(0, 2))
CTkLabel(screen_dashboard, text="Your money, uncovered.", font=("Arial", 26, "bold"), text_color=("#0F172A", "#F8FAFC")).pack(anchor="w", pady=(0, 2))
CTkLabel(screen_dashboard, text="A clear view of the recurring payments quietly leaving your account.", font=("Arial", 13), text_color=("#64748B", "#94A3B8")).pack(anchor="w", pady=(0, 15))


def calculate_dashboard_metrics(commitments):
    total_monthly = 0.0
    total_annual = 0.0

    for item in commitments:
        raw_amt = str(item.get("amount", "0")).replace("₹", "").replace(",", "").strip()
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


def create_card(parent, icon_filename, default_symbol, icon_bg, label_text, value_text, footer_text):
    card = CTkFrame(parent, fg_color=("#FFFFFF", "#1E293B"), corner_radius=16)

    img_icon = load_icon(icon_filename, (20, 20)) if icon_filename else None

    if img_icon:
        icon_badge = CTkLabel(
            card,
            text="",
            image=img_icon,
            fg_color=icon_bg,
            width=36,
            height=36,
            corner_radius=10,
        )
    else:
        icon_badge = CTkLabel(
            card,
            text=default_symbol,
            font=("Arial", 16, "bold"),
            fg_color=icon_bg,
            text_color="#0F172A",
            width=36,
            height=36,
            corner_radius=10,
        )
    icon_badge.pack(anchor="w", padx=20, pady=(15, 10))

    lbl = CTkLabel(card, text=label_text, font=("Arial", 12), text_color=("#64748B", "#94A3B8"))
    lbl.pack(anchor="w", padx=20, pady=(0, 4))

    val = CTkLabel(card, text=value_text, font=("Arial", 24, "bold"), text_color=("#0F172A", "#F8FAFC"))
    val.pack(anchor="w", padx=20, pady=(0, 4))

    foot = CTkLabel(card, text=footer_text, font=("Arial", 11), text_color=("#94A3B8", "#64748B"))
    foot.pack(anchor="w", padx=20, pady=(0, 15))

    return card


metrics = calculate_dashboard_metrics(commitments_data)

cards_frame = CTkFrame(screen_dashboard, fg_color="transparent")
cards_frame.pack(fill="x", pady=(0, 15))

for i in range(3):
    cards_frame.grid_columnconfigure(i, weight=1)

card1 = create_card(cards_frame, "recurring.png", "🔄", "#E2E8F0", "Monthly recurring spend", metrics["monthly_str"], "Across identified commitments")
card1.grid(row=0, column=0, padx=(0, 10), sticky="ew")

card2 = create_card(cards_frame, "annual.png", "₹", "#DCFCE7", "Annual commitment", metrics["annual_str"], "Your recurring baseline")
card2.grid(row=0, column=1, padx=5, sticky="ew")

card3 = create_card(cards_frame, "subscriptions.png", "✓", "#E0F2FE", "Active subscriptions", metrics["active_str"], metrics["merchants_footer"])
card3.grid(row=0, column=2, padx=(10, 0), sticky="ew")

# --- DASHBOARD MATPLOTLIB CHARTS FRAME ---
charts_frame = CTkFrame(screen_dashboard, fg_color="transparent")
charts_frame.pack(fill="x", pady=(5, 10))
charts_frame.grid_columnconfigure(0, weight=3)
charts_frame.grid_columnconfigure(1, weight=2)

# CHART 1: RECURRING SPEND TREND
chart1_card = CTkFrame(charts_frame, fg_color=("#FFFFFF", "#1E293B"), corner_radius=16)
chart1_card.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

chart1_header = CTkFrame(chart1_card, fg_color="transparent")
chart1_header.pack(fill="x", padx=20, pady=(15, 2))

CTkLabel(chart1_header, text="Recurring spend trend", font=("Arial", 15, "bold"), text_color=("#0F172A", "#F8FAFC")).pack(side="left")

trend_range_var = StringVar(value="Last 6 months")
trend_dropdown = CTkOptionMenu(
    chart1_header,
    values=["Last 6 months", "Last 12 months", "All time"],
    variable=trend_range_var,
    font=("Arial", 11),
    width=125,
    height=28,
    corner_radius=6,
    fg_color=("#F1F5F9", "#334155"),
    text_color=("#334155", "#F8FAFC"),
    button_color=("#F1F5F9", "#334155"),
    button_hover_color=("#E2E8F0", "#475569"),
    dropdown_fg_color=("#FFFFFF", "#1E293B"),
    dropdown_text_color=("#0F172A", "#F8FAFC"),
    command=lambda choice: update_trend_chart(choice),
)
trend_dropdown.pack(side="right")

CTkLabel(chart1_card, text="Monthly run-rate from detected commitments", font=("Arial", 11), text_color=("#94A3B8", "#64748B")).pack(anchor="w", padx=20, pady=(0, 10))

all_monthly_sums = {}
for item in commitments_data:
    for h in item.get("history", []):
        m_key = h["date"][:7]
        raw_val = float(str(h["amount"]).replace("₹", "").replace(",", "").strip() or 0)
        all_monthly_sums[m_key] = all_monthly_sums.get(m_key, 0.0) + raw_val

if not all_monthly_sums:
    all_monthly_sums = {"2025-03": 649.0, "2025-04": 649.0, "2025-05": 1648.0, "2025-06": 1648.0, "2025-07": 1798.0, "2025-08": 1798.0, "2025-09": 999.0}

fig1, ax1 = plt.subplots(figsize=(5.5, 2.6), dpi=100)

canvas1 = FigureCanvasTkAgg(fig1, master=chart1_card)
canvas1.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))

annot1 = ax1.annotate(
    "",
    xy=(0, 0),
    xytext=(15, 15),
    textcoords="offset points",
    bbox=dict(boxstyle="round,pad=0.5", fc="#FFFFFF", ec="#CBD5E1", lw=1),
    arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0", color="#10B981"),
    fontsize=9,
    fontweight="bold",
    color="#0F172A",
)
annot1.set_visible(False)

current_trend_data = {"months": [], "vals": [], "sc": None, "max_val": 1000}


def format_month_label(m_str):
    try:
        dt = datetime.strptime(m_str, "%Y-%m")
        return dt.strftime("%b '%y")
    except Exception:
        return m_str


def update_trend_chart(range_choice):
    ax1.clear()
    annot1.set_visible(False)

    is_dark = get_appearance_mode().lower() == "dark"
    bg_color = "#1E293B" if is_dark else "#FFFFFF"
    text_color = "#F8FAFC" if is_dark else "#0F172A"
    subtext_color = "#94A3B8" if is_dark else "#64748B"
    grid_color = "#334155" if is_dark else "#E2E8F0"

    fig1.patch.set_facecolor(bg_color)
    ax1.set_facecolor(bg_color)

    annot1.get_bbox_patch().set_facecolor(bg_color)
    annot1.get_bbox_patch().set_edgecolor("#475569" if is_dark else "#CBD5E1")
    annot1.set_color(text_color)

    sorted_all = sorted(all_monthly_sums.keys())

    if range_choice == "Last 6 months":
        filtered_keys = sorted_all[-6:]
    elif range_choice == "Last 12 months":
        filtered_keys = sorted_all[-12:]
    else:
        filtered_keys = sorted_all

    m_labels = [format_month_label(k) for k in filtered_keys]
    s_vals = [all_monthly_sums[k] for k in filtered_keys]
    x_idx = np.arange(len(filtered_keys))

    ax1.plot(x_idx, s_vals, color='#10B981', linewidth=2.5)
    ax1.fill_between(x_idx, s_vals, color='#10B981', alpha=0.15)
    sc_scatter = ax1.scatter(x_idx, s_vals, color='#10B981', s=35, zorder=5)

    max_v = max(s_vals) if s_vals else 1000
    ax1.set_ylim(bottom=0, top=max_v * 1.35)
    ax1.set_xlim(-0.4, len(x_idx) - 0.6 + 0.4)

    ax1.set_xticks(x_idx)
    rotation_angle = 30 if len(filtered_keys) > 8 else 0
    ax1.set_xticklabels(m_labels, fontsize=8, color=subtext_color, rotation=rotation_angle)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda val, pos: f"₹{int(val):,}"))
    ax1.tick_params(axis='y', labelsize=8, labelcolor=subtext_color)

    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_color(grid_color)
    ax1.spines['bottom'].set_color(grid_color)
    ax1.grid(axis='y', linestyle='--', alpha=0.3, color=grid_color)
    fig1.tight_layout()

    ax1.add_artist(annot1)

    current_trend_data["months"] = filtered_keys
    current_trend_data["vals"] = s_vals
    current_trend_data["sc"] = sc_scatter
    current_trend_data["max_val"] = max_v

    canvas1.draw_idle()


def hover_line(event):
    if event.inaxes == ax1 and current_trend_data["sc"] is not None:
        cont, ind = current_trend_data["sc"].contains(event)
        if cont:
            idx = ind["ind"][0]
            pos = current_trend_data["sc"].get_offsets()[idx]
            annot1.xy = pos

            months_list = current_trend_data["months"]
            vals_list = current_trend_data["vals"]
            max_v = current_trend_data["max_val"]

            x_ratio = idx / max(1, len(months_list) - 1)
            offset_x = -115 if x_ratio > 0.70 else 15
            offset_y = -35 if pos[1] > (max_v * 0.75) else 15

            annot1.set_position((offset_x, offset_y))
            text = f"{months_list[idx]}\namount : ₹{int(vals_list[idx]):,}"
            annot1.set_text(text)
            annot1.set_visible(True)
            canvas1.draw_idle()
            return
    if annot1.get_visible():
        annot1.set_visible(False)
        canvas1.draw_idle()


canvas1.mpl_connect("motion_notify_event", hover_line)

# CHART 2: WHERE IT GOES
chart2_card = CTkFrame(charts_frame, fg_color=("#FFFFFF", "#1E293B"), corner_radius=16)
chart2_card.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

CTkLabel(chart2_card, text="Where it goes", font=("Arial", 15, "bold"), text_color=("#0F172A", "#F8FAFC")).pack(anchor="w", padx=20, pady=(15, 2))
CTkLabel(chart2_card, text="Monthly by category", font=("Arial", 11), text_color=("#94A3B8", "#64748B")).pack(anchor="w", padx=20, pady=(0, 10))

cat_totals = {}
for item in commitments_data:
    cat = item.get("category", "Utilities")
    raw_val = float(str(item.get("amount", "0")).replace("₹", "").replace(",", "").strip() or 0)
    freq = str(item.get("frequency", "monthly")).lower()
    m_val = raw_val if freq == "monthly" else (raw_val / 12.0 if freq == "annual" else raw_val / 3.0)
    cat_totals[cat] = cat_totals.get(cat, 0.0) + m_val

categories = list(cat_totals.keys())
cat_amounts = [cat_totals[c] for c in categories]
max_cat_amt = max(cat_amounts) if cat_amounts else 1000

fig2, ax2 = plt.subplots(figsize=(4.2, 2.6), dpi=100)
canvas2 = FigureCanvasTkAgg(fig2, master=chart2_card)
canvas2.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))

annot2 = ax2.annotate(
    "",
    xy=(0, 0),
    xytext=(15, -10),
    textcoords="offset points",
    bbox=dict(boxstyle="round,pad=0.5", fc="#FFFFFF", ec="#CBD5E1", lw=1),
    fontsize=9,
    fontweight="bold",
    color="#0F172A",
)
annot2.set_visible(False)

bars = []


def render_category_chart():
    global bars
    ax2.clear()
    annot2.set_visible(False)

    is_dark = get_appearance_mode().lower() == "dark"
    bg_color = "#1E293B" if is_dark else "#FFFFFF"
    bar_color = "#38BDF8" if is_dark else "#1E293B"
    text_color = "#F8FAFC" if is_dark else "#0F172A"
    subtext_color = "#CBD5E1" if is_dark else "#475569"

    fig2.patch.set_facecolor(bg_color)
    ax2.set_facecolor(bg_color)

    annot2.get_bbox_patch().set_facecolor(bg_color)
    annot2.get_bbox_patch().set_edgecolor("#475569" if is_dark else "#CBD5E1")
    annot2.set_color(text_color)

    y_pos = np.arange(len(categories))
    bars = ax2.barh(y_pos, cat_amounts, height=0.45, color=bar_color, edgecolor="none")

    ax2.set_xlim(left=0, right=max_cat_amt * 1.35)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(categories, fontsize=9, color=subtext_color)
    ax2.tick_params(axis="y", pad=12)

    ax2.invert_yaxis()
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.spines["left"].set_visible(False)
    ax2.spines["bottom"].set_visible(False)
    ax2.xaxis.set_visible(False)
    fig2.tight_layout()

    ax2.add_artist(annot2)
    canvas2.draw_idle()


def hover_bar(event):
    if event.inaxes == ax2:
        for idx, bar in enumerate(bars):
            if bar.contains(event)[0]:
                y = bar.get_y() + bar.get_height() / 2.0
                x = bar.get_width()
                annot2.xy = (x, y)

                if x > (max_cat_amt * 0.65):
                    annot2.set_position((-115, -10))
                else:
                    annot2.set_position((15, -10))

                text = f"{categories[idx]}\namount : ₹{int(round(cat_amounts[idx])):,}"
                annot2.set_text(text)
                annot2.set_visible(True)
                canvas2.draw_idle()
                return
    if annot2.get_visible():
        annot2.set_visible(False)
        canvas2.draw_idle()


canvas2.mpl_connect("motion_notify_event", hover_bar)

# Initial chart renders
update_trend_chart("Last 6 months")
render_category_chart()


# ==========================================
# --- SCREEN 2: TRANSACTIONS ---
# ==========================================
screen_transactions = CTkFrame(screens_container, fg_color="transparent")

tx_list_container = CTkFrame(screen_transactions, fg_color="transparent")
tx_list_container.pack(fill="both", expand=True)

tx_details_container = CTkScrollableFrame(screen_transactions, fg_color=("#F8FAFC", "#0F172A"))

CTkLabel(tx_list_container, text="DISCOVERY", font=("Arial", 11, "bold"), text_color=("#94A3B8", "#64748B")).pack(anchor="w", pady=(0, 2))
top_title_frame = CTkFrame(tx_list_container, fg_color="transparent")
top_title_frame.pack(fill="x", pady=(0, 2))
CTkLabel(top_title_frame, text="All commitments", font=("Arial", 26, "bold"), text_color=("#0F172A", "#F8FAFC")).pack(side="left", anchor="w")
CTkLabel(tx_list_container, text="Every recurring payment we found in your synthetic transaction history.", font=("Arial", 13), text_color=("#64748B", "#94A3B8")).pack(anchor="w", pady=(0, 15))

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
    fg_color=("#FFFFFF", "#1E293B"),
    border_width=1,
    border_color=("#E2E8F0", "#334155"),
    text_color=("#0F172A", "#F8FAFC"),
    placeholder_text_color=("#94A3B8", "#64748B"),
)
tx_search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

category_options = ["All categories", "Education", "Entertainment", "Health", "Insurance", "Productivity", "Shopping", "Utilities"]
category_dropdown = CTkOptionMenu(
    filter_frame,
    values=category_options,
    variable=category_var,
    font=("Arial", 12),
    height=38,
    corner_radius=8,
    fg_color=("#FFFFFF", "#1E293B"),
    text_color=("#334155", "#F8FAFC"),
    button_color=("#FFFFFF", "#1E293B"),
    button_hover_color=("#F1F5F9", "#334155"),
    dropdown_fg_color=("#FFFFFF", "#1E293B"),
    dropdown_text_color=("#0F172A", "#F8FAFC"),
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
    fg_color=("#FFFFFF", "#1E293B"),
    text_color=("#334155", "#F8FAFC"),
    button_color=("#FFFFFF", "#1E293B"),
    button_hover_color=("#F1F5F9", "#334155"),
    dropdown_fg_color=("#FFFFFF", "#1E293B"),
    dropdown_text_color=("#0F172A", "#F8FAFC"),
)
frequency_dropdown.pack(side="left", padx=(0, 15))

count_label = CTkLabel(filter_frame, text="0 found", font=("Arial", 12), text_color=("#64748B", "#94A3B8"))
count_label.pack(side="left")

headers_frame = CTkFrame(tx_list_container, fg_color="transparent")
headers_frame.pack(fill="x", padx=15, pady=(0, 8))
headers_frame.grid_columnconfigure(0, weight=4)
headers_frame.grid_columnconfigure(1, weight=3)
headers_frame.grid_columnconfigure(2, weight=3)
headers_frame.grid_columnconfigure(3, weight=2)

CTkLabel(headers_frame, text="MERCHANT", font=("Arial", 11, "bold"), text_color=("#94A3B8", "#64748B")).grid(row=0, column=0, sticky="w")
CTkLabel(headers_frame, text="AMOUNT / FREQUENCY", font=("Arial", 11, "bold"), text_color=("#94A3B8", "#64748B")).grid(row=0, column=1, sticky="w")
CTkLabel(headers_frame, text="LAST PAYMENT", font=("Arial", 11, "bold"), text_color=("#94A3B8", "#64748B")).grid(row=0, column=2, sticky="w")
CTkLabel(headers_frame, text="CONFIDENCE", font=("Arial", 11, "bold"), text_color=("#94A3B8", "#64748B")).grid(row=0, column=3, sticky="e")

commitments_scroll = CTkScrollableFrame(tx_list_container, fg_color=("#F8FAFC", "#0F172A"), corner_radius=0)
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

    back_btn = CTkButton(
        tx_details_container,
        text="←  All commitments",
        font=("Arial", 12, "bold"),
        text_color="#0D9488",
        fg_color="transparent",
        hover_color=("#F1F5F9", "#334155"),
        anchor="w",
        height=28,
        command=show_list_view,
    )
    back_btn.pack(anchor="w", pady=(0, 10))

    CTkLabel(tx_details_container, text="INVESTIGATION", font=("Arial", 11, "bold"), text_color=("#94A3B8", "#64748B")).pack(anchor="w", pady=(0, 2))
    CTkLabel(tx_details_container, text=item["name"], font=("Arial", 28, "bold"), text_color=("#0F172A", "#F8FAFC")).pack(anchor="w", pady=(0, 2))

    descriptor = item["name"].upper().replace(" ", "")
    CTkLabel(tx_details_container, text=f"{descriptor} · evidence-based recurring payment review", font=("Arial", 12), text_color=("#64748B", "#94A3B8")).pack(anchor="w", pady=(0, 18))

    hero_card = CTkFrame(tx_details_container, fg_color=("#FFFFFF", "#1E293B"), corner_radius=12, border_width=1, border_color=("#F1F5F9", "#334155"))
    hero_card.pack(fill="x", pady=(0, 16))

    hero_left = CTkFrame(hero_card, fg_color="transparent")
    hero_left.pack(side="left", padx=20, pady=20)

    badge = CTkLabel(hero_left, text=item["initial"], font=("Arial", 20, "bold"), fg_color=item["bg"], text_color="#1E293B", width=52, height=52, corner_radius=12)
    badge.pack(side="left", padx=(0, 16))

    hero_info = CTkFrame(hero_left, fg_color="transparent")
    hero_info.pack(side="left")

    amt_freq_frame = CTkFrame(hero_info, fg_color="transparent")
    amt_freq_frame.pack(anchor="w")

    CTkLabel(amt_freq_frame, text=item["amount"], font=("Arial", 22, "bold"), text_color=("#0F172A", "#F8FAFC")).pack(side="left")
    CTkLabel(amt_freq_frame, text=f" /{item['frequency']}", font=("Arial", 13), text_color=("#64748B", "#94A3B8")).pack(side="left", padx=(2, 0))

    CTkLabel(hero_info, text=f"Estimated next payment: {item['date']}", font=("Arial", 11), text_color=("#64748B", "#94A3B8")).pack(anchor="w", pady=(2, 6))

    conf_badge = CTkLabel(hero_info, text="HIGH CONFIDENCE", font=("Arial", 9, "bold"), fg_color="#DCFCE7", text_color="#166534", corner_radius=6, padx=8, pady=2)
    conf_badge.pack(anchor="w")

    hero_right = CTkFrame(hero_card, fg_color="transparent")
    hero_right.pack(side="right", padx=25, pady=20)

    raw_amt = float(item["amount"].replace("₹", "").replace(",", "").strip() or 0)
    freq_str = item["frequency"].lower()
    annual_cost = raw_amt if freq_str == "annual" else (raw_amt * 4 if freq_str == "quarterly" else raw_amt * 12)

    CTkLabel(hero_right, text="Annual cost", font=("Arial", 11), text_color=("#94A3B8", "#64748B"), anchor="e").pack(anchor="e")
    CTkLabel(hero_right, text=f"₹{int(round(annual_cost)):,}", font=("Arial", 20, "bold"), text_color=("#0F172A", "#F8FAFC"), anchor="e").pack(anchor="e")

    history_list = item.get("history", [])
    if not history_list and cursor:
        try:
            search_kw = item["name"].split()[0]
            cursor.execute("SELECT transaction_date::text, description, amount::float FROM transactions WHERE description ILIKE %s AND transaction_type = 'debit' ORDER BY transaction_date ASC;", (f"%{search_kw}%",))
            rows = cursor.fetchall()
            if rows:
                history_list = [{"date": r[0][:10], "description": r[1], "amount": f"₹{int(r[2]):,}" if float(r[2]).is_integer() else f"₹{r[2]:,.2f}"} for r in rows]
        except Exception as e:
            print(f"History fetch error: {e}")

    if not history_list:
        history_list = [{"date": item["date"], "description": item["name"].upper(), "amount": item["amount"]}]

    history_card = CTkFrame(tx_details_container, fg_color=("#FFFFFF", "#1E293B"), corner_radius=12, border_width=1, border_color=("#F1F5F9", "#334155"))
    history_card.pack(fill="x", pady=(0, 16), padx=1)

    CTkLabel(history_card, text="Payment history", font=("Arial", 15, "bold"), text_color=("#0F172A", "#F8FAFC")).pack(anchor="w", padx=20, pady=(15, 2))
    CTkLabel(history_card, text=f"Matched {len(history_list)} payment{'s' if len(history_list) != 1 else ''} for {item['name']} with a {item['frequency']} billing pattern.", font=("Arial", 12), text_color=("#64748B", "#94A3B8"), wraplength=700, justify="left").pack(anchor="w", padx=20, pady=(0, 15))

    for idx, hist in enumerate(history_list):
        is_latest = idx == (len(history_list) - 1)
        hist_row = CTkFrame(history_card, fg_color="transparent")
        hist_row.pack(fill="x", padx=20, pady=6)

        hist_left = CTkFrame(hist_row, fg_color="transparent")
        hist_left.pack(side="left")

        CTkLabel(hist_left, text="•", font=("Arial", 16, "bold"), text_color="#10B981").pack(side="left", padx=(0, 10))
        CTkLabel(hist_left, text=hist["date"], font=("Arial", 12, "bold"), text_color=("#334155", "#CBD5E1")).pack(side="left", padx=(0, 20))
        CTkLabel(hist_left, text=hist.get("description", item["name"].upper()), font=("Arial", 11), text_color=("#64748B", "#94A3B8")).pack(side="left")

        hist_right = CTkFrame(hist_row, fg_color="transparent")
        hist_right.pack(side="right")
        CTkLabel(hist_right, text=hist["amount"], font=("Arial", 13, "bold"), text_color=("#0F172A", "#F8FAFC")).pack(side="left", padx=(0, 8))

        if is_latest:
            CTkLabel(hist_right, text="Latest", font=("Arial", 10, "bold"), fg_color="#DCFCE7", text_color="#166534", corner_radius=6, padx=6, pady=1).pack(side="left")

        if not is_latest:
            CTkFrame(history_card, fg_color=("#F8FAFC", "#334155"), height=1).pack(fill="x", padx=20, pady=(2, 2))

    CTkFrame(history_card, fg_color="transparent", height=10).pack()

    cancel_card = CTkFrame(tx_details_container, fg_color=("#FFFFFF", "#1E293B"), corner_radius=12, border_width=1, border_color=("#F1F5F9", "#334155"))
    cancel_card.pack(fill="x", pady=(0, 20), ipadx=10, ipady=10)

    CTkLabel(cancel_card, text="GUIDED CANCELLATION", font=("Arial", 11, "bold"), text_color=("#94A3B8", "#64748B")).pack(anchor="w", padx=20, pady=(15, 2))
    CTkLabel(cancel_card, text="How to stop this payment", font=("Arial", 16, "bold"), text_color=("#0F172A", "#F8FAFC")).pack(anchor="w", padx=20, pady=(0, 10))

    pay_mech = item.get("payment_mechanism", "Card recurring")
    CTkLabel(cancel_card, text=f"  ✓  Payment mechanism: {pay_mech}  ", font=("Arial", 11, "bold"), fg_color=("#F1F5F9", "#334155"), text_color=("#334155", "#F8FAFC"), corner_radius=8, height=32).pack(anchor="w", padx=20, pady=(0, 15))

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

        CTkLabel(step_row, text=str(idx), font=("Arial", 11, "bold"), fg_color=("#0F172A", "#F8FAFC"), text_color=("#FFFFFF", "#0F172A"), width=22, height=22, corner_radius=11).pack(side="left", padx=(0, 12), anchor="n")
        CTkLabel(step_row, text=step_text, font=("Arial", 12), text_color=("#334155", "#CBD5E1"), anchor="w", wraplength=650, justify="left").pack(side="left", fill="x", expand=True)

    warning_box = CTkFrame(cancel_card, fg_color="#FEF3C7", corner_radius=8, border_width=1, border_color="#FDE68A")
    warning_box.pack(fill="x", padx=20, pady=(18, 15))

    warn_inner = CTkFrame(warning_box, fg_color="transparent")
    warn_inner.pack(fill="x", padx=12, pady=10)

    CTkLabel(warn_inner, text="⚠️", font=("Arial", 14)).pack(side="left", anchor="n", padx=(0, 8))
    warn_text = "Important distinction: Revoking a mandate may stop future debits but does not automatically terminate the underlying merchant contract."
    CTkLabel(warn_inner, text=warn_text, font=("Arial", 11, "bold"), text_color="#92400E", wraplength=650, justify="left").pack(side="left", fill="x", expand=True)


def render_commitments(items):
    for widget in commitments_scroll.winfo_children():
        widget.destroy()

    count_label.configure(text=f"{len(items)} found")

    for item in items:
        row_card = CTkFrame(commitments_scroll, fg_color=("#FFFFFF", "#1E293B"), corner_radius=10, height=58)
        row_card.pack(fill="x", pady=4, padx=2)
        row_card.pack_propagate(False)

        left_box = CTkFrame(row_card, fg_color="transparent")
        left_box.pack(side="left", padx=12)

        badge = CTkLabel(left_box, text=item["initial"], font=("Arial", 14, "bold"), fg_color=item.get("bg", "#E0F2FE"), text_color="#1E293B", width=36, height=36, corner_radius=8)
        badge.pack(side="left", padx=(0, 12))

        text_box = CTkFrame(left_box, fg_color="transparent")
        text_box.pack(side="left")

        name_lbl = CTkLabel(text_box, text=item["name"], font=("Arial", 13, "bold"), text_color=("#0F172A", "#F8FAFC"), anchor="w")
        name_lbl.pack(anchor="w")

        sub_lbl = CTkLabel(text_box, text=f"{item['frequency']} · {item['category']}", font=("Arial", 11), text_color=("#64748B", "#94A3B8"), anchor="w")
        sub_lbl.pack(anchor="w")

        right_box = CTkFrame(row_card, fg_color="transparent")
        right_box.pack(side="right", padx=15)

        val_box = CTkFrame(right_box, fg_color="transparent")
        val_box.pack(side="left", padx=(0, 15))

        amt_lbl = CTkLabel(val_box, text=item["amount"], font=("Arial", 13, "bold"), text_color=("#0F172A", "#F8FAFC"), anchor="e")
        amt_lbl.pack(anchor="e")

        dt_lbl = CTkLabel(val_box, text=item["date"], font=("Arial", 11), text_color=("#64748B", "#94A3B8"), anchor="e")
        dt_lbl.pack(anchor="e")

        chevron = CTkLabel(right_box, text="›", font=("Arial", 18), text_color=("#94A3B8", "#64748B"))
        chevron.pack(side="right")

        bind_click_recursive(row_card, lambda e, it=item: open_commitment_details(it))


def filter_commitments(*args):
    q = tx_search_var.get().lower().strip()
    cat = category_var.get()
    freq = frequency_var.get()

    filtered = []
    for item in commitments_data:
        matches_q = not q or (q in item["name"].lower() or q in item["category"].lower() or q in item["frequency"].lower())
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

CTkLabel(screen_alerts, text="SIGNALS", font=("Arial", 11, "bold"), text_color=("#94A3B8", "#64748B")).pack(anchor="w", pady=(0, 2))
CTkLabel(screen_alerts, text="Alerts & insights", font=("Arial", 26, "bold"), text_color=("#0F172A", "#F8FAFC")).pack(anchor="w", pady=(0, 2))
CTkLabel(screen_alerts, text="Understand what changed before it quietly costs you more.", font=("Arial", 13), text_color=("#64748B", "#94A3B8")).pack(anchor="w", pady=(0, 15))

alerts_scroll = CTkScrollableFrame(screen_alerts, fg_color=("#F8FAFC", "#0F172A"), corner_radius=0)
alerts_scroll.pack(fill="both", expand=True)


def parse_amount_value(amt_str):
    raw = str(amt_str).replace("₹", "").replace(",", "").strip()
    try:
        return float(raw)
    except ValueError:
        return 0.0


def calculate_dynamic_alerts(commitments):
    alerts = []
    for item in commitments:
        name = item.get("name", "Merchant")
        history = item.get("history", [])

        if len(history) >= 2:
            for i in range(1, len(history)):
                prev_amt = parse_amount_value(history[i - 1].get("amount", "0"))
                curr_amt = parse_amount_value(history[i].get("amount", "0"))

                if prev_amt > 0 and curr_amt > prev_amt:
                    pct = int(round(((curr_amt - prev_amt) / prev_amt) * 100))
                    alerts.append({
                        "title": f"{name} price increased",
                        "subtitle": f"Your recurring charge changed from {history[i-1]['amount']} to {history[i]['amount']}.",
                        "merchant": name,
                        "date": history[i]["date"],
                        "change": f"{history[i-1]['amount']} → {history[i]['amount']} (+{pct}%)",
                        "item": item,
                    })
                elif prev_amt == 0 and curr_amt > 0:
                    alerts.append({
                        "title": f"Free trial converted",
                        "subtitle": f"A free trial for {name} was followed by a {history[i]['amount']} recurring subscription charge.",
                        "merchant": name,
                        "date": history[i]["date"],
                        "change": f"₹0 → {history[i]['amount']}",
                        "item": item,
                    })
        elif len(history) == 1:
            alerts.append({
                "title": f"New recurring payment started",
                "subtitle": f"A new recurring commitment of {item['amount']} was detected for {name}.",
                "merchant": name,
                "date": item["date"],
                "change": f"New ({item['amount']})",
                "item": item,
            })

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
        CTkLabel(alerts_scroll, text="No alerts detected in your transaction history.", font=("Arial", 14), text_color=("#64748B", "#94A3B8")).pack(pady=40)
        return

    grouped = {}
    for alert in alerts_data:
        d = alert["date"]
        grouped.setdefault(d, []).append(alert)

    for d_str in sorted(grouped.keys(), reverse=True):
        sep_frame = CTkFrame(alerts_scroll, fg_color="transparent")
        sep_frame.pack(fill="x", pady=(12, 8))

        CTkFrame(sep_frame, fg_color=("#E2E8F0", "#334155"), height=1).pack(side="left", fill="x", expand=True, padx=(0, 10))
        CTkLabel(sep_frame, text=f"───  {format_date_label(d_str)}  ───", font=("Arial", 11, "bold"), text_color=("#64748B", "#94A3B8")).pack(side="left")
        CTkFrame(sep_frame, fg_color=("#E2E8F0", "#334155"), height=1).pack(side="right", fill="x", expand=True, padx=(10, 0))

        for alert in grouped[d_str]:
            card = CTkFrame(alerts_scroll, fg_color=("#FFFFFF", "#1E293B"), corner_radius=12, border_width=1, border_color=("#F1F5F9", "#334155"))
            card.pack(fill="x", pady=5, padx=2)

            left_frame = CTkFrame(card, fg_color="transparent")
            left_frame.pack(side="left", padx=15, pady=15)

            CTkLabel(left_frame, text="⚠️", font=("Arial", 14), fg_color="#FEF2F2", text_color="#0F172A", width=36, height=36, corner_radius=18).pack(side="left", padx=(0, 12))

            text_box = CTkFrame(left_frame, fg_color="transparent")
            text_box.pack(side="left")

            CTkLabel(text_box, text=alert["title"], font=("Arial", 13, "bold"), text_color=("#0F172A", "#F8FAFC"), anchor="w").pack(anchor="w")
            CTkLabel(text_box, text=alert["subtitle"], font=("Arial", 11), text_color=("#64748B", "#94A3B8"), anchor="w", wraplength=450, justify="left").pack(anchor="w")

            right_frame = CTkFrame(card, fg_color="transparent")
            right_frame.pack(side="right", padx=15, pady=15)

            CTkLabel(right_frame, text=f"Merchant: {alert['merchant']}   Observed: {alert['date']}   Change: {alert['change']}", font=("Arial", 11), text_color=("#64748B", "#94A3B8")).pack(side="left", padx=(0, 15))

            investigate_btn = CTkButton(
                right_frame,
                text="Investigate ↗",
                font=("Arial", 12, "bold"),
                text_color="#0D9488",
                fg_color="transparent",
                hover_color=("#F1F5F9", "#334155"),
                width=100,
                height=32,
                command=lambda item=alert["item"]: navigate_to_investigation(item),
            )
            investigate_btn.pack(side="right")


def navigate_to_investigation(target_item):
    select_menu("Transactions")
    open_commitment_details(target_item)


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
    for screen in screens.values():
        screen.grid_forget()

    screens[selected_name].grid(row=0, column=0, sticky="nsew")

    if selected_name == "Transactions":
        show_list_view()

    header_title.configure(text="Overview" if selected_name == "Dashboard" else selected_name)

    for name, btn in menu_buttons.items():
        if name == selected_name:
            btn.configure(fg_color="#1814F3", text_color="#FFFFFF")
        else:
            btn.configure(fg_color="transparent", text_color=("#718EBF", "#94A3B8"))


menu_options = ["Dashboard", "Transactions", "Alerts & Insights"]

for name in menu_options:
    btn = CTkButton(
        sidebar,
        text=name,
        font=("Arial", 14, "bold"),
        corner_radius=12,
        fg_color="transparent",
        text_color=("#718EBF", "#94A3B8"),
        hover_color=("#E0E7FF", "#334155"),
        anchor="w",
        height=42,
        command=lambda n=name: select_menu(n),
    )
    btn.pack(fill="x", padx=15, pady=6)
    menu_buttons[name] = btn

# Set default tab
select_menu("Dashboard")


# ==========================================
# 5. CLEAN CLOSE PROTOCOL
# ==========================================
def on_closing():
    plt.close('all')
    app.quit()
    app.destroy()


app.protocol("WM_DELETE_WINDOW", on_closing)

app.mainloop()

if connection:
    connection.close()
