import flet as ft
import mysql.connector
from mysql.connector import Error
import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_invoice_pdf(invoice_id, items, total):
    file_path = f"invoice_{invoice_id}.pdf"

    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph(f"Invoice #{invoice_id}", styles["Title"]))
    elements.append(Spacer(1, 10))

    for item in items:
        elements.append(
            Paragraph(
                f"{item['description']} | Qty {item['quantity']} | ₹{item['unit_price']}",
                styles["Normal"]
            )
        )

    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"Total: ₹{total}", styles["Heading2"]))

    doc.build(elements)

    return file_path
# =====================================================================
# 1. DATABASE CONNECTION & CORE UTILITIES
# =====================================================================
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost", 
            user="root", 
            password="root", 
            database="hospital"
        )
        return conn
    except Error as e:
        print(f"CRITICAL: Database Connection Failed: {e}")
        return None

def get_query_data(query, params=None):
    conn = get_db_connection()
    if not conn: 
        return []
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        data = cursor.fetchall()
        return data
    except Error as e:
        print(f"SQL Read Error: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def execute_query(query, params):
    conn = get_db_connection()
    if not conn: 
        return False
    
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        return True
    except Error as e:
        print(f"SQL Write Error: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def execute_transaction(queries_with_params):
    """Executes multiple queries safely in one transactional block."""
    conn = get_db_connection()
    if not conn: 
        return False
    
    cursor = conn.cursor()
    try:
        for query, params in queries_with_params:
            cursor.execute(query, params)
        conn.commit()
        return True
    except Error as e:
        print(f"Transaction Error: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

# =========================
# LAB HELPERS  ✅ ADD HERE
# =========================
def fmt_dt(v):
    return str(v)[:16] if v else "N/A"

def priority_bg(priority_value):
    if priority_value == "STAT":
        return ft.Colors.RED_500
    if priority_value == "Urgent":
        return ft.Colors.ORANGE_500
    return ft.Colors.GREEN_500

def status_bg(status_value):
    if status_value == "Completed":
        return ft.Colors.GREEN_700
    if status_value == "Processing":
        return ft.Colors.BLUE_700
    if status_value == "Sample Collected":
        return ft.Colors.ORANGE_700
    if status_value == "Cancelled":
        return ft.Colors.RED_700
    return ft.Colors.GREY_700

def make_invoice_number():
    return f"PH-INV-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

def get_medicine_category_groups():
    meds = get_query_data("""
        SELECT
            m.medicine_id,
            m.medicine_name,
            m.generic_name,
            m.brand_name,
            COALESCE(c.category_name, 'Uncategorized') AS category_name,
            m.dosage_form,
            m.strength,
            m.unit_price,
            m.stock_quantity,
            m.reorder_level,
            m.expiry_date,
            m.storage_condition,
            m.prescription_required
        FROM Medicine m
        LEFT JOIN MedicineCategory c ON m.category_id = c.category_id
        ORDER BY category_name, m.medicine_name
    """)
    groups = {}
    for m in meds or []:
        cat = m.get("category_name") or "Uncategorized"
        groups.setdefault(cat, []).append(m)
    return meds or [], groups




# =====================================================================
# 2. MAIN APPLICATION ARCHITECTURE
# =====================================================================
def main(page: ft.Page):
    # App Configuration
    page.title = "MR HOSPITALS | Enterprise Command Center"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_full_screen = True
    page.update()
    page.padding = 0
    page.spacing = 0

    # Universal UI Button Styles
    admin_btn_style = ft.ButtonStyle(
        color=ft.Colors.WHITE, 
        bgcolor=ft.Colors.TEAL_700, 
        shape=ft.RoundedRectangleBorder(radius=8)
    )
    
    rec_btn_style = ft.ButtonStyle(
        color=ft.Colors.WHITE, 
        bgcolor=ft.Colors.TEAL_700, 
        shape=ft.RoundedRectangleBorder(radius=8)
    )

    # Universal Navigation & Feedback Helpers
    def nav_to(tab_name):
        page.session.store.set("active_tab", tab_name)
        page.views.clear()
        page.views.append(dashboard_view())
        page.update()

    def logout_action(e):
        page.session.store.clear()
        page.views.clear()
        page.views.append(login_view())
        page.update()

    def show_snack(message, color):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE), 
            bgcolor=color
        )
        page.snack_bar.open = True
        page.update()

    # =====================================================================
    # 3. DYNAMIC STAFF HIRING LOGIC (WITH AUTO EMP-ID)
    # =====================================================================
    def register_patient_db(data):
            conn = get_db_connection()
            if not conn:
                return False

            cursor = conn.cursor()
            try:
                cursor.execute("SELECT role_id FROM Role WHERE role_name=%s", ("Patient",))
                role_record = cursor.fetchone()
                if not role_record:
                    return False

                role_id = role_record[0]

                cursor.execute("""
                    INSERT INTO Users (username, u_password, email, role_id, is_active)
                    VALUES (%s, %s, %s, %s, TRUE)
                """, (data["user"], data["pass"], data["email"], role_id))

                uid = cursor.lastrowid
                reg_no = f"APL-PT-{uid:04d}"

                cursor.execute("""
                    INSERT INTO Patient (
                        user_id, registration_no, first_name, last_name, gender,
                        date_of_birth, blood_group, phone, email, address,
                        city, state, pincode,
                        emergency_contact_name, emergency_contact_phone, emergency_contact_rel,
                        insurance_provider, insurance_policy_no, registered_by
                    )
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    uid,
                    reg_no,
                    data["fname"],
                    data["lname"],
                    data["gender"],
                    data["dob"] or None,
                    data["bg"],
                    data["phone"],
                    data["email"],
                    data["addr"],
                    data["city"],
                    data["state"],
                    data["pincode"],
                    data["emg_name"],
                    data["emg_phone"],
                    data["emg_rel"],
                    data["ins_provider"],
                    data["ins_policy"],
                    data.get("registered_by")
                ))

                conn.commit()
                return True

            except Exception as e:
                print("Patient Register Error:", e)
                conn.rollback()
                return False
            finally:
                cursor.close()
                conn.close()
    def hire_staff_db(data):

        conn = get_db_connection()
        if not conn:
            return False

        cursor = conn.cursor()
        
        def safe_date(value):
            return value if value else None
   
        try:
            # 🔹 Role ID
            cursor.execute("SELECT role_id FROM Role WHERE role_name = %s", (data['role'],))
            role_record = cursor.fetchone()
            if not role_record:
                return False

            role_id = role_record[0]

            # 🔹 Insert into Users
            cursor.execute("""
                INSERT INTO Users (username, u_password, email, role_id, is_active)
                VALUES (%s, %s, %s, %s, TRUE)
            """, (data['user'], data['pass'], data['email'], role_id))

            uid = cursor.lastrowid

            emp_id = f"EMP-{data['role'][:3].upper()}-{uid:04d}"

            # 🔹 ROLE BASED INSERT
            if data['role'] == "Doctor":
                cursor.execute("""
                    INSERT INTO Doctor (
                        user_id, first_name, last_name, gender, date_of_birth, phone, email,
                        specialization, qualification, license_number, experience_years,
                        dept_id, consultation_fee, shift, joining_date, blood_group, address
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    uid,
                    data['fname'], data['lname'],
                    data['gender'],
                    safe_date(data['dob']),
                    data['phone'], data['email'],
                    data.get('spec'),
                    data.get('qual'),
                    data.get('lic'),
                    int(data['exp']) if data.get('exp') else None,
                    int(data['dept']) if data.get('dept') else None,
                    float(data['fee']) if data.get('fee') else None,
                    data['shift'],
                    safe_date(data['join']),
                    data.get('bg'),
                    data.get('addr')
                ))

            elif data['role'] == "Admin":
                cursor.execute("""
                    INSERT INTO Admin (user_id, first_name, last_name, phone, employee_id, access_level)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (uid, data['fname'], data['lname'], data['phone'], emp_id, data.get('access')))

            elif data['role'] == "Receptionist":
                cursor.execute("""
                    INSERT INTO Receptionist (
                        user_id, first_name, last_name, gender, phone,
                        employee_id, shift, counter_number, joining_date
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    uid,
                    data['fname'], data['lname'], data['gender'], data['phone'],
                    emp_id, data['shift'],
                    int(data.get('counter')) if data.get('counter') else None,
                    safe_date(data['join'])
                ))

            elif data['role'] == "Lab Technician":
                cursor.execute("""
                    INSERT INTO LabTechnician (
                        user_id, first_name, last_name, gender, phone,
                        employee_id, qualification, specialization, shift, joining_date
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    uid,
                    data['fname'], data['lname'], data['gender'], data['phone'],
                    emp_id,
                    data.get('qual'),
                    data.get('spec'),
                    data['shift'],
                    safe_date(data['join'])
                ))

            elif data['role'] == "Pharmacist":
                cursor.execute("""
                    INSERT INTO Pharmacist (
                        user_id, first_name, last_name, license_number, phone, shift
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    uid,
                    data['fname'], data['lname'],
                    data.get('lic'),
                    data['phone'], data['shift']
                ))

            conn.commit()
            return True

        except Exception as e:
            print("Hire Error DB:", e)
            conn.rollback()
            return False

        finally:
            cursor.close()
            conn.close()

    # =====================================================================
    # 4. VIEW: SECURE LOGIN GATEKEEPER
    # =====================================================================
    def login_view():
        username_input = ft.TextField(
            label="Username", 
            width=320, 
            border_radius=10, 
            prefix_icon=ft.Icons.PERSON,
            filled=True,
            bgcolor="#EDF2F7"
        )
        
        password_input = ft.TextField(
            label="Password", 
            password=True, 
            width=320, 
            border_radius=10, 
            can_reveal_password=True, 
            prefix_icon=ft.Icons.LOCK,
            filled=True,
            bgcolor="#EDF2F7"
        )
        
        error_msg = ft.Text("", color=ft.Colors.RED)

        def handle_login(e):
            query = """
                SELECT u.user_id, u.username, r.role_name 
                FROM Users u 
                JOIN Role r ON u.role_id = r.role_id 
                WHERE u.username=%s AND u.u_password=%s AND u.is_active=TRUE
            """
            data = get_query_data(query, (username_input.value, password_input.value))
            
            if data:
                user = data[0]
                page.session.store.set("user_id", user['user_id'])
                page.session.store.set("username", user['username'])
                page.session.store.set("role", user['role_name'])
                
                # Role-Based Context Setup
                if user['role_name'] == "Admin": 
                    page.session.store.set("active_tab", "admin_overview")
                
                elif user['role_name'] == "Receptionist": 
                    rec_query = "SELECT receptionist_id FROM Receptionist WHERE user_id=%s"
                    rec_data = get_query_data(rec_query, (user['user_id'],))
                    if rec_data: 
                        page.session.store.set("rec_id", rec_data[0]['receptionist_id'])
                    page.session.store.set("active_tab", "rec_overview")
                elif user['role_name'] == "Doctor":
                    doc_query = "SELECT doctor_id FROM Doctor WHERE user_id=%s"
                    doc_data = get_query_data(doc_query, (user['user_id'],))
                    if doc_data:
                        page.session.store.set("doctor_id", doc_data[0]['doctor_id'])
                    page.session.store.set("active_tab", "doctor_dashboard")

                elif user['role_name'] == "Lab Technician":
                    lab_query = "SELECT lab_tech_id FROM LabTechnician WHERE user_id=%s"
                    lab_data = get_query_data(lab_query, (user['user_id'],))
                    if lab_data:
                        page.session.store.set("lab_tech_id", lab_data[0]['lab_tech_id'])
                    page.session.store.set("active_tab", "lab_dashboard")    

                # in login_view handle_login
                elif user['role_name'] == "Pharmacist":
                    pharm_query = "SELECT pharmacist_id FROM Pharmacist WHERE user_id=%s"
                    pharm_data = get_query_data(pharm_query, (user['user_id'],))
                    if pharm_data:
                        page.session.store.set("pharmacist_id", pharm_data[0]['pharmacist_id'])
                    page.session.store.set("active_tab", "pharma_dashboard")  

                elif user['role_name'] == "Patient":
                    pat_query = "SELECT patient_id FROM Patient WHERE user_id=%s"
                    pat_data = get_query_data(pat_query, (user['user_id'],))
                    if pat_data:
                        page.session.store.set("patient_id", pat_data[0]['patient_id'])
                    page.session.store.set("active_tab", "patient_dashboard")

                else: 
                    page.session.store.set("active_tab", "unauthorized")
                
                # Execute Route
                page.views.clear()
                page.views.append(dashboard_view())
                page.update()
            else:
                error_msg.value = "Authentication Failed. Check credentials."
                page.update()

        # ---------------- LEFT SIDE (IMAGE + BRANDING) ----------------
        left_section = ft.Container(
    expand=True,
    margin=0,
    padding=0,
    content=ft.Column(
        expand=True,
        spacing=0,
        controls=[

            # ✅ TOP IMAGE
            ft.Container(
                expand=3,   # 🔥 70% space
                width=float("inf"),
                content=ft.Image(
                    src="Image.png",
                    fit="cover",
                    expand=True,
                ),
            ),

            # ✅ BOTTOM TEAL SECTION
            ft.Container(
                expand=2,   # 🔥 30% space
                width=float("inf"),
                bgcolor="#38A169",
                padding=40,
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    spacing=10,
                    controls=[
                        ft.Text(
                            "Welcome to",
                            size=34,
                            weight="bold",
                            color="white",
                        ),
                        ft.Text(
                            "MR HOSPITALS",
                            size=60,
                            weight="bold",
                            color="white"
                        ),
                        ft.Text(
                            "Smart Healthcare • EHR • HMS",
                            size=24,
                            color="#CCFBF1"
                        ),
                    ]
                )
            ),
        ]
    )
)

        # ---------------- RIGHT SIDE (LOGIN FORM) ----------------
        login_section = ft.Container(
            expand=True,
            bgcolor="#FFFFFF",
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(
                        ft.Icons.LOCAL_HOSPITAL_ROUNDED, 
                        size=60, 
                        color="#38A169"
                    ),

                    ft.Text(
                        "MR HOSPITALS", 
                        size=30, 
                        weight="bold", 
                        color="#38A169"
                    ),

                    ft.Text(
                        "Login to continue",
                        size=14,
                        color="#718096"
                    ),

                    ft.Container(height=20),

                    username_input,
                    password_input,
                    error_msg,

                    ft.Container(height=10),

                    ft.FilledButton(
                        "Login", 
                        color="#FFFFFF",
                        bgcolor="#1A202C",
                        on_click=handle_login, 
                        width=320, 
                        height=50, 
                        style=admin_btn_style
                    )
                ]
            )
        )

        # ---------------- FINAL VIEW ----------------
        return ft.View(
            route="/login",
            controls=[
                ft.Row(
                    expand=True,
                    spacing=0,
                    controls=[
                        left_section,
                        login_section
                    ]
                )
            ]
        )

    # =====================================================================
    # 5. VIEW: MASTER DASHBOARD ENGINE
    # =====================================================================
    def dashboard_view():
        uid = page.session.store.get("user_id")
        user_name = page.session.store.get("username")
        role = page.session.store.get("role")
        tab = page.session.store.get("active_tab")
        def handle_discharge(e):
            if not source_dd.value:
                show_snack("Select IPD admission first", ft.Colors.RED)
                return

            try:
                aid = int(source_dd.value)
            except:
                show_snack("Invalid admission selected", ft.Colors.RED)
                return

            generate_discharge_bill(aid)
        def update_order_status(order_id, new_status):
            execute_query(
                "UPDATE LabOrder SET status=%s WHERE order_id=%s",
                (new_status, order_id)
            )
            show_snack("Order status updated", ft.Colors.GREEN)
            nav_to("lab_orders")

        def make_invoice_number(prefix="APL"):
            return f"{prefix}-INV-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

        def safe_float(v, default=0.0):
            try:
                return float(v)
            except:
                return default

        def save_invoice_record(
            patient_id,
            bill_type,
            items,
            collect_now=False,
            payment_mode=None,
            notes="",
            consultation_id=None,
            lab_order_id=None,
            dispense_id=None,
            admission_id=None,
        ):
            if not items:
                raise Exception("No bill items found")

            conn = get_db_connection()
            if not conn:
                return None

            cursor = conn.cursor()
            try:
                subtotal = round(sum(safe_float(i["quantity"]) * safe_float(i["unit_price"]) for i in items), 2)
                discount = 0.0
                tax = 0.0
                total = round(subtotal - discount + tax, 2)

                paid_amount = total if collect_now else 0.0
                due_amount = round(total - paid_amount, 2)
                payment_status = "Paid" if collect_now else "Unpaid"
                print("DEBUG VALUES:")
                print(patient_id, admission_id, dispense_id)
                print("ITEMS:", items)

                cursor.execute("""
                    INSERT INTO Invoice (
                        invoice_number, patient_id, admission_id, generated_by,
                        invoice_date, subtotal, discount, tax, total_amount,
                        paid_amount, due_amount, payment_status, payment_mode, notes,
                        bill_type, consultation_id, lab_order_id, dispense_id
                    )
                    VALUES (%s, %s, %s, %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    make_invoice_number(),
                    patient_id,
                    admission_id,
                    1,   # ✅ FIXED (NO uid ERROR)
                    subtotal,
                    discount,
                    tax,
                    total,
                    paid_amount,
                    due_amount,
                    payment_status,
                    payment_mode if collect_now else None,
                    notes,
                    "PHARMACY",   # ✅ FORCE VALUE
                    consultation_id,
                    lab_order_id,
                    dispense_id
                ))

                invoice_id = cursor.lastrowid

                for item in items:
                    cursor.execute("""
                        INSERT INTO InvoiceItem (
                            invoice_id, item_type, description, quantity, unit_price, total_price
                        )
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        invoice_id,
                        item["item_type"],
                        item["description"],
                        item["quantity"],
                        item["unit_price"],
                        round(safe_float(item["quantity"]) * safe_float(item["unit_price"]), 2)
                    ))

                conn.commit()
                return invoice_id
            except Exception as e:
                conn.rollback()
                print("INVOICE ERROR:", e)   # 🔥 ADD THIS
                show_snack(f"Invoice Error: {e}", ft.Colors.RED)
                return None
            finally:
                cursor.close()
                conn.close()

        def generate_discharge_bill(admission_id):

            # =========================
            # 1. GET PATIENT
            # =========================
            adm = get_query_data("""
                SELECT patient_id, admission_date, discharge_date
                FROM Admission
                WHERE admission_id = %s
            """, (admission_id,))

            if not adm:
                show_snack("Admission not found", ft.Colors.RED)
                return

            patient_id = adm[0]["patient_id"]

            items = []

            # =========================
            # 2. ROOM CHARGES
            # =========================
            room = get_query_data("""
                SELECT r.room_number, r.daily_charge,
                    a.admission_date, a.discharge_date
                FROM Admission a
                JOIN Bed b ON a.bed_id = b.bed_id
                JOIN Room r ON b.room_id = r.room_id
                WHERE a.admission_id = %s
            """, (admission_id,))

            if room:
                r = room[0]

                days = 1
                if r["discharge_date"]:
                    days = (r["discharge_date"].date() - r["admission_date"].date()).days or 1

                items.append({
                    "item_type": "Room",
                    "description": f"Room {r['room_number']} ({days} days)",
                    "quantity": days,
                    "unit_price": float(r["daily_charge"])
                })

            # =========================
            # 3. LAB CHARGES
            # =========================
            labs = get_query_data("""
                SELECT t.test_name, t.price
                FROM LabOrder lo
                JOIN LabOrderItem li ON lo.order_id = li.order_id
                JOIN LabTest t ON li.test_id = t.test_id
                WHERE lo.patient_id = %s
                AND lo.consultation_id IS NOT NULL
            """, (patient_id,))

            for l in (labs or []):
                items.append({
                    "item_type": "Lab",
                    "description": l["test_name"],
                    "quantity": 1,
                    "unit_price": float(l["price"])
                })

            # =========================
            # 4. PHARMACY CHARGES
            # =========================
            meds = get_query_data("""
                SELECT m.medicine_name, di.quantity, di.unit_price
                FROM PharmacyDispense pd
                JOIN DispenseItem di ON pd.dispense_id = di.dispense_id
                JOIN Medicine m ON di.medicine_id = m.medicine_id
                WHERE pd.patient_id = %s
            """, (patient_id,))

            for m in (meds or []):
                items.append({
                    "item_type": "Medicine",
                    "description": m["medicine_name"],
                    "quantity": int(m["quantity"]),
                    "unit_price": float(m["unit_price"])
                })

            # =========================
            # 5. CONSULTATION
            # =========================
            consult = get_query_data("""
                SELECT d.first_name, d.last_name, d.consultation_fee
                FROM Consultation c
                JOIN Doctor d ON c.doctor_id = d.doctor_id
                WHERE c.patient_id = %s
            """, (patient_id,))

            for c in (consult or []):
                items.append({
                    "item_type": "Consultation",
                    "description": f"Dr. {c['first_name']} {c['last_name']}",
                    "quantity": 1,
                    "unit_price": float(c["consultation_fee"])
                })

            # =========================
            # 6. CHECK EMPTY
            # =========================
            if not items:
                show_snack("No billable items found", ft.Colors.RED)
                return

            # =========================
            # 7. SAVE FINAL INVOICE
            # =========================
            invoice_id = save_invoice_record(
                patient_id=patient_id,
                bill_type="IPD",
                items=items,
                collect_now=False,
                payment_mode=None,
                notes=f"Final Discharge Bill (Admission {admission_id})",
                admission_id=admission_id
            )

            if invoice_id:
                show_snack("Discharge bill generated", ft.Colors.GREEN)
            else:
                show_snack("Failed to generate bill", ft.Colors.RED)        

        def mark_invoice_paid(invoice_id, mode):
            conn = get_db_connection()
            if not conn:
                return

            cursor = conn.cursor()
            try:
                cursor.execute("""
                    UPDATE Invoice
                    SET paid_amount = total_amount,
                        due_amount = 0,
                        payment_status = 'Paid',
                        status = 'Paid',
                        payment_mode = %s
                    WHERE invoice_id = %s
                """, (mode, invoice_id))
                conn.commit()
                show_snack("Invoice marked as paid", ft.Colors.GREEN)
                nav_to("billing")
            except Exception as e:
                conn.rollback()
                show_snack(f"Payment error: {e}", ft.Colors.RED)
            finally:
                cursor.close()
                conn.close()
            
        # ----------------------
        # ---------------------------------------
        # 5.1. DYNAMIC ROLE-BASED SIDEBAR
        # -------------------------------------------------------------
        # -----------------------------

        sidebar_controls = []
        sidebar_bg = "#004D40"

        if role == "Admin":
            level_data = get_query_data("SELECT access_level FROM Admin WHERE user_id = %s", (uid,))
            level = level_data[0]['access_level'] if level_data else "standard"

            sidebar_controls = [
                ft.Text("COMMAND CENTER", color="white", weight="bold", size=20),
                ft.Divider(color="white24"),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.ANALYTICS, color="white"),
                    title=ft.Text("Overview", color="white"),
                    on_click=lambda _: nav_to("admin_overview")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.PEOPLE_ALT, color="white"),
                    title=ft.Text("Manage Staff", color="white"),
                    on_click=lambda _: nav_to("staff")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.SCHEDULE, color="white"),
                    title=ft.Text("Staff Schedules", color="white"),
                    on_click=lambda _: nav_to("schedules")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.PERSON_SEARCH, color="white"),
                    title=ft.Text("Patients Directory", color="white"),
                    on_click=lambda _: nav_to("patients")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.MEDICATION, color="white"),
                    title=ft.Text("Pharmacy Inventory", color="white"),
                    on_click=lambda _: nav_to("meds")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.DOMAIN, color="white"),
                    title=ft.Text("Facility Management", color="white"),
                    on_click=lambda _: nav_to("rooms")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.PAYMENTS, color="white"),
                    title=ft.Text("Billing Overview", color="white"),
                    on_click=lambda _: nav_to("billing")
                ),
                ft.Container(expand=True),
                ft.Container(
                    bgcolor="white10",
                    padding=15,
                    border_radius=10,
                    content=ft.Text(f"Admin: {user_name}\nAccess: {level.upper()}", color="white", size=12)
                ),
                ft.TextButton(
                    "Secure Logout",
                    icon=ft.Icons.LOGOUT,
                    on_click=logout_action,
                    style=ft.ButtonStyle(color="white70")
                )
            ]

        elif role == "Doctor":
            sidebar_bg = "#004D40"
            sidebar_controls = [
                ft.Text("DOCTOR PANEL", color="white", weight="bold", size=20),
                ft.Divider(color="white24"),
                ft.ListTile(title=ft.Text("OPD Queue", color="white"), on_click=lambda _: nav_to("doctor_dashboard")),
                ft.ListTile(title=ft.Text("Admitted Patients", color="white"), on_click=lambda _: nav_to("doctor_ipd")),
                ft.ListTile(title=ft.Text("Patient Medical Profile", color="white"), on_click=lambda _: nav_to("doctor_patient")),
                ft.ListTile(title=ft.Text("Consultation", color="white"), on_click=lambda _: nav_to("doctor_consult")),
                ft.ListTile(title=ft.Text("Prescriptions", color="white"), on_click=lambda _: nav_to("doctor_prescription")),
                ft.ListTile(title=ft.Text("Lab Orders", color="white"), on_click=lambda _: nav_to("doctor_lab")),
                ft.ListTile(title=ft.Text("Discharge", color="white"), on_click=lambda _: nav_to("doctor_discharge")),
                ft.Container(expand=True),

                ft.TextButton(
                    "Logout",
                    icon=ft.Icons.LOGOUT,
                    on_click=logout_action,
                    style=ft.ButtonStyle(color="white70")
                )
            ]

        elif role == "Lab Technician":
            sidebar_bg = "#004D40"
            sidebar_controls = [
                ft.Text("LAB PANEL", size=22, weight="bold", color="white"),
                ft.Divider(color="white24"),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.DASHBOARD, color="white"),
                    title=ft.Text("Lab Dashboard", color="white"),
                    on_click=lambda _: nav_to("lab_dashboard")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.SCIENCE, color="white"),
                    title=ft.Text("Test Catalog", color="white"),
                    on_click=lambda _: nav_to("lab_catalog")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.LIST_ALT, color="white"),
                    title=ft.Text("Lab Orders", color="white"),
                    on_click=lambda _: nav_to("lab_orders")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.EDIT, color="white"),
                    title=ft.Text("Enter Result", color="white"),
                    on_click=lambda _: nav_to("lab_enter_result")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.HISTORY, color="white"),
                    title=ft.Text("Result History", color="white"),
                    on_click=lambda _: nav_to("lab_history")
                ),
                ft.Container(expand=True),

                ft.TextButton(
                    "Logout",
                    icon=ft.Icons.LOGOUT,
                    on_click=logout_action,
                    style=ft.ButtonStyle(color="white70")
                )
            ]

        elif role == "Pharmacist":
            sidebar_bg = "#004D40"
            sidebar_controls = [
                ft.Text("PHARMACY PANEL", color="white", weight="bold", size=20),
                ft.Divider(color="white24"),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.DASHBOARD, color="white"),
                    title=ft.Text("Dashboard", color="white"),
                    on_click=lambda _: nav_to("pharma_dashboard")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.INVENTORY_2, color="white"),
                    title=ft.Text("Inventory", color="white"),
                    on_click=lambda _: nav_to("pharma_inventory")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.RECEIPT_LONG, color="white"),
                    title=ft.Text("Prescriptions", color="white"),
                    on_click=lambda _: nav_to("pharma_prescriptions")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.MEDICAL_INFORMATION, color="white"),
                    title=ft.Text("Dispense", color="white"),
                    on_click=lambda _: nav_to("pharma_dispense")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.PAYMENTS, color="white"),
                    title=ft.Text("Invoices", color="white"),
                    on_click=lambda _: nav_to("pharma_invoice")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.HISTORY, color="white"),
                    title=ft.Text("Sales History", color="white"),
                    on_click=lambda _: nav_to("pharma_sales")
                ),
                ft.Container(expand=True),

                ft.TextButton(
                    "Logout",
                    icon=ft.Icons.LOGOUT,
                    on_click=logout_action,
                    style=ft.ButtonStyle(color="white70")
                )
            ]

        elif role == "Receptionist":
            sidebar_bg = ft.Colors.TEAL_900
            sidebar_controls = [
                ft.Text("FRONT DESK", color="white", weight="bold", size=20),
                ft.Divider(color="white24"),
                ft.ListTile(leading=ft.Icon(ft.Icons.HOME, color="white"), title=ft.Text("Desk Overview", color="white"), on_click=lambda _: nav_to("rec_overview")),
                ft.ListTile(leading=ft.Icon(ft.Icons.PERSON_ADD, color="white"), title=ft.Text("Register Patient", color="white"), on_click=lambda _: nav_to("reg_patient")),
                ft.ListTile(leading=ft.Icon(ft.Icons.CALENDAR_MONTH, color="white"), title=ft.Text("Appointments Desk", color="white"), on_click=lambda _: nav_to("book_appt")),
                ft.ListTile(leading=ft.Icon(ft.Icons.BED, color="white"), title=ft.Text("IPD Admissions", color="white"), on_click=lambda _: nav_to("admissions")),
                ft.ListTile(leading=ft.Icon(ft.Icons.RECEIPT_LONG, color="white"), title=ft.Text("Billing Desk", color="white"), on_click=lambda _: nav_to("rec_billing")),
                ft.ListTile(leading=ft.Icon(ft.Icons.FORMAT_LIST_BULLETED, color="white"), title=ft.Text("All Patients", color="white"), on_click=lambda _: nav_to("patients")),
                ft.Container(expand=True),
                ft.Container(
                    bgcolor="white10",
                    padding=15,
                    border_radius=10,
                    content=ft.Text(f"Staff: {user_name}\nRole: Receptionist", color="white", size=12)
                ),
                ft.TextButton(
                    "Secure Logout",
                    icon=ft.Icons.LOGOUT,
                    on_click=logout_action,
                    style=ft.ButtonStyle(color="white70")
                )
            ]

        elif role == "Patient":
            sidebar_bg = "#004D40"
            sidebar_controls = [
                ft.Text("PATIENT PORTAL", color="white", weight="bold", size=20),
                ft.Divider(color="white24"),
                ft.ListTile(leading=ft.Icon(ft.Icons.DASHBOARD, color="white"), title=ft.Text("Dashboard", color="white"), on_click=lambda _: nav_to("patient_dashboard")),
                ft.ListTile(leading=ft.Icon(ft.Icons.PERSON, color="white"), title=ft.Text("My Profile", color="white"), on_click=lambda _: nav_to("patient_profile")),
                ft.ListTile(leading=ft.Icon(ft.Icons.EVENT_NOTE, color="white"), title=ft.Text("Appointments", color="white"), on_click=lambda _: nav_to("patient_appointments")),
                ft.ListTile(leading=ft.Icon(ft.Icons.MEDICAL_SERVICES, color="white"), title=ft.Text("Medical History", color="white"), on_click=lambda _: nav_to("patient_history")),
                ft.ListTile(leading=ft.Icon(ft.Icons.WARNING_AMBER, color="white"), title=ft.Text("Allergies", color="white"), on_click=lambda _: nav_to("patient_allergies")),
                ft.ListTile(leading=ft.Icon(ft.Icons.SCIENCE, color="white"), title=ft.Text("Lab Results", color="white"), on_click=lambda _: nav_to("patient_lab_results")),
                ft.ListTile(leading=ft.Icon(ft.Icons.RECEIPT_LONG, color="white"), title=ft.Text("Bills & Payments", color="white"), on_click=lambda _: nav_to("patient_billing")),
                ft.Container(expand=True),

                ft.TextButton(
                    "Logout",
                    icon=ft.Icons.LOGOUT,
                    on_click=logout_action,
                    style=ft.ButtonStyle(color="white70")
                )
            ]

        sidebar = ft.Container(
            width=280,
            bgcolor=sidebar_bg,
            padding=20,
            content=ft.Column(controls=sidebar_controls)
        )

        nice_titles = {
            "admin_overview": "Enterprise Dashboard",
            "rec_overview": "Front Desk Operations",
            "reg_patient": "Comprehensive Patient Registration",
            "book_appt": "Appointment Scheduling & Queue",
            "admissions": "IPD Admissions & Bed Allocation",
            "rec_billing": "Patient Billing & Invoicing",
            "staff": "Human Resources & Staff Directory",
            "schedules": "Enterprise Staff Schedules",
            "patients": "Global Patient Directory",
            "meds": "Pharmacy Inventory Control",
            "rooms": "Wards, Rooms & Bed Configuration",
            "billing": "Billing Overview",
            "lab_dashboard": "Lab Technician Dashboard",
            "lab_catalog": "Test Catalog",
            "lab_orders": "Lab Orders",
            "lab_enter_result": "Enter Lab Result",
            "lab_history": "Result History",
            "pharma_dashboard": "Pharmacy Dashboard",
            "pharma_inventory": "Medicine Inventory",
            "pharma_prescriptions": "Doctor Prescriptions",
            "pharma_dispense": "Dispense Medicines",
            "pharma_invoice": "Pharmacy Invoice",
            "pharma_sales": "Pharmacy Sales",
            "patient_dashboard": "Patient Dashboard",
            "patient_profile": "My Profile",
            "patient_appointments": "Appointments",
            "patient_history": "Medical History",
            "patient_allergies": "Allergies",
            "patient_lab_results": "Lab Results",
            "patient_billing": "Bills & Payments",
        }

        header_banner = ft.Container(
            padding=ft.Padding.only(bottom=20),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.LOCAL_HOSPITAL, 
                                size=45, 
                                color="#004D40" if role == "Admin" else "#004D40"
                            ),
                            ft.Text(
                                "MR HOSPITALS", 
                                size=32, 
                                weight="w900", 
                                color="#004D40" if role == "Admin" else "#004D40"
                            )
                        ]
                    ),
                    ft.FilledButton(
                        "Export Report PDF", 
                        icon=ft.Icons.PICTURE_AS_PDF, 
                        style=admin_btn_style if role == "Admin" else rec_btn_style
                    )
                ]
            )
        )

        content_controls = [
            header_banner, 
            ft.Text(
                nice_titles.get(tab, tab), 
                size=28, 
                weight="bold", 
                color=ft.Colors.GREY_800
            ), 
            ft.Divider(height=30)
        ]
        
        
        # =====================================================================
        # 5.3. MODULE: OVERVIEW DASHBOARDS
        # =====================================================================
        if tab == "admin_overview":
            banner = ft.Container(
                bgcolor="#004D40", 
                padding=40, 
                border_radius=15, 
                margin=ft.Margin.only(),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("MR HOSPITALS DASHBOARD", size=32, weight="bold", color=ft.Colors.WHITE), 
                                ft.Text("Enterprise Operations & Resource Management", size=16, color=ft.Colors.WHITE70)
                            ]
                        ), 
                        ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, size=100, color=ft.Colors.WHITE24)
                    ]
                )
            )
            content_controls.append(banner)
            
            revenue_card = ft.Card(
                ft.Container(
                    padding=25, 
                    width=320, 
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text("REVENUE YTD", color=ft.Colors.GREY_600), 
                                    ft.Text("₹4,50,000", size=26, weight="bold")
                                ]
                            ), 
                            ft.Icon(ft.Icons.TRENDING_UP, color=ft.Colors.GREEN, size=40)
                        ]
                    )
                )
            )
            
            ward_card = ft.Card(
                ft.Container(
                    padding=25, 
                    width=320, 
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text("WARD OCCUPANCY", color=ft.Colors.GREY_600), 
                                    ft.Text("85%", size=26, weight="bold")
                                ]
                            ), 
                            ft.Stack(
                                controls=[
                                    ft.ProgressRing(value=0.85, color=ft.Colors.ORANGE, bgcolor=ft.Colors.GREY_200, width=50, height=50), 
                                    ft.Container(padding=15, content=ft.Icon(ft.Icons.BED, size=20, color=ft.Colors.ORANGE))
                                ]
                            )
                        ]
                    )
                )
            )
            
            content_controls.append(
                ft.Row(
                    controls=[revenue_card, ward_card]
                )
            )
        elif tab == "doctor_dashboard":
            doctor_id = page.session.store.get("doctor_id")
            pid = page.session.store.get("selected_patient_id")

            if pid:
                p = get_query_data("SELECT first_name, last_name FROM Patient WHERE patient_id=%s", (pid,))
                if p:
                    content_controls.append(
                        ft.Container(
                            padding=10,
                            bgcolor="#F0FDFA",
                            content=ft.Text(f"Current Patient: {p[0]['first_name']} {p[0]['last_name']}")
                        )
                    )

            appts = get_query_data("""
                SELECT a.appointment_id,a.patient_id, p.first_name, p.last_name,
                    a.appointment_time, a.reason, a.status
                FROM Appointment a
                JOIN Patient p ON a.patient_id = p.patient_id
                WHERE a.doctor_id = %s
                ORDER BY a.appointment_date DESC
            """, (doctor_id,))

            rows = [
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(a['appointment_id']))),

                        ft.DataCell(
                            ft.TextButton(
                                f"{a['first_name']} {a['last_name']}",
                                style=ft.ButtonStyle(color="#0F766E"),
                                on_click=lambda e, pid=a['patient_id']: (
                                    page.session.store.set("selected_patient_id", pid),
                                    nav_to("doctor_patient")
                                )
                            )
                        ),

                        ft.DataCell(ft.Text(str(a['appointment_time']))),
                        ft.DataCell(ft.Text(a['reason'] or "")),
                        ft.DataCell(ft.Text(a['status']))
                    ]
                )
                for a in appts
            ]

            content_controls.append(
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("ID")),
                        ft.DataColumn(ft.Text("Patient")),
                        ft.DataColumn(ft.Text("Time")),
                        ft.DataColumn(ft.Text("Reason")),
                        ft.DataColumn(ft.Text("Status")),
                    ],
                    rows=rows
                )
            )
        elif tab == "doctor_ipd":
            pid = page.session.store.get("selected_patient_id")

            if pid:
                p = get_query_data("SELECT first_name, last_name FROM Patient WHERE patient_id=%s", (pid,))
                if p:
                    content_controls.append(
                        ft.Container(
                            padding=10,
                            bgcolor="#F0FDFA",
                            content=ft.Text(f"Current Patient: {p[0]['first_name']} {p[0]['last_name']}")
                        )
                    )
            doctor_id = page.session.store.get("doctor_id")

            data = get_query_data("""
                SELECT a.admission_id, p.first_name, b.bed_number, w.ward_name, a.status
                FROM Admission a
                JOIN Patient p ON a.patient_id = p.patient_id
                JOIN Bed b ON a.bed_id = b.bed_id
                JOIN Room r ON b.room_id = r.room_id
                JOIN Ward w ON r.ward_id = w.ward_id
                WHERE a.doctor_id = %s
            """, (doctor_id,))

            content_controls.append(
                ft.Column([
                    ft.Text(f"{d['first_name']} | Bed {d['bed_number']} | {d['ward_name']} | {d['status']}")
                    for d in data
                ])
            )
        elif tab == "doctor_consult":

            pid = page.session.store.get("selected_patient_id")

            if not pid:
                content_controls.append(ft.Text("Select patient first"))
                return

            # 🔹 Patient Banner
            p = get_query_data("SELECT first_name, last_name FROM Patient WHERE patient_id=%s", (pid,))
            if p:
                content_controls.append(
                    ft.Container(
                        padding=10,
                        bgcolor="#F0FDFA",
                        content=ft.Text(f"Current Patient: {p[0]['first_name']} {p[0]['last_name']}")
                    )
                )

            # 🔹 Consultation Fields
            chief = ft.TextField(label="Chief Complaint")
            symptoms = ft.TextField(label="Symptoms")
            diagnosis = ft.TextField(label="Diagnosis")

            def save_consult(e):
                doc_id = page.session.store.get("doctor_id")

                execute_query("""
                    INSERT INTO Consultation 
                    (patient_id, doctor_id, chief_complaint, symptoms, diagnosis)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    pid,
                    doc_id,
                    chief.value,
                    symptoms.value,
                    diagnosis.value
                ))

                show_snack("Consultation Saved", ft.Colors.GREEN)

            content_controls.append(
                ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Text("Consultation Panel", size=20, weight="bold"),
                        chief,
                        symptoms,
                        diagnosis,
                        ft.FilledButton("Save Consultation", on_click=save_consult, bgcolor="#0F766E", color="white")
                    ])
                )
            )
           
        elif tab == "doctor_discharge":
            pid = page.session.store.get("selected_patient_id")

            if pid:
                p = get_query_data("SELECT first_name, last_name, admission_id FROM Patient join Admission ON Patient.patient_id = Admission.patient_id WHERE Patient.patient_id=%s",
                                    (pid,))
                if p:
                    content_controls.append(
                        ft.Container(
                            padding=10,
                            bgcolor="#F0FDFA",
                            content=ft.Text(f"Current Patient: {p[0]['first_name']} {p[0]['last_name']}")
                        )
                    )
            admission_id = ft.Dropdown(label="Admission ID", width=300)
            notes = ft.TextField(label="Discharge Notes")
            selected_patient_id = pid  
            admissions = get_query_data("""
                SELECT a.admission_id, p.first_name, p.last_name,p.registration_no
                FROM Admission a 
                JOIN Patient p ON a.patient_id = p.patient_id
                WHERE a.status = 'Admitted' and p.patient_id = %s
            """, (selected_patient_id,))

            
            # admission_id = ft.Dropdown(
            #     label="Admission ID",
            #     width=300,
            #     options=[
            #         ft.dropdown.Option(
            #             key=str(a["admission_id"]),
            #             text=f'{a["admission_id"]} - {a["first_name"]} {a["last_name"]} ({a["registration_no"]})'
            #         )
            #         for a in admissions
            #     ]
            # )
            if admissions:
                options = [
                    ft.dropdown.Option(
                        key=str(a["admission_id"]),
                        text=f'{a["admission_id"]} - {a["first_name"]} {a["last_name"]} ({a["registration_no"]})'
                    )
                    for a in admissions
                ]
            else:
                options = [
                    ft.dropdown.Option(
                        key="none",
                        text="No active admission found"
                    )
                ]

            admission_id = ft.Dropdown(
                label="Admission ID",
                width=350,
                options=options
            )
            notes = ft.TextField(label="Discharge Notes")

            admissions = get_query_data("""
                SELECT admission_id 
                FROM Admission 
                WHERE status = 'Admitted'
            """)

            admission_id = ft.Dropdown(
                label="Admission ID",
                width=300,
                options=[
                    ft.dropdown.Option(str(a["admission_id"]))
                    for a in admissions
                ]
            )

            notes = ft.TextField(label="Discharge Notes")

            def discharge(e):
                if not admission_id.value:
                    show_snack("Select admission first", ft.Colors.RED)
                    return

                aid = int(admission_id.value)

                conn = get_db_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT due_amount FROM Invoice WHERE admission_id=%s
                """, (aid,))

                data = cursor.fetchone()

                if data and float(data[0]) > 0:
                    show_snack("Clear pending bill before discharge", ft.Colors.RED)
                    return

                cursor.execute("""
                    UPDATE Admission
                    SET status='Discharged',
                        discharge_date=NOW(),
                        discharge_notes=%s
                    WHERE admission_id=%s
                """, (notes.value, aid))

                conn.commit()
                show_snack("Patient discharged successfully", ft.Colors.GREEN)

            content_controls.append(
                ft.Column([
                    admission_id,
                    notes,
                    ft.FilledButton("Discharge Patient",bgcolor="#0F766E", color="white", on_click=discharge)
                ])
            ) 
        elif tab == "doctor_patient":
            pid = page.session.store.get("selected_patient_id")

            if not pid:
                content_controls.append(ft.Text("No patient selected"))
                return

            patient = get_query_data("SELECT * FROM Patient WHERE patient_id=%s", (pid,))
            if not patient:
                content_controls.append(ft.Text("Patient not found"))
                return

            p = patient[0]

            patient_banner = get_query_data(
                "SELECT first_name, last_name FROM Patient WHERE patient_id=%s",
                (pid,)
            )
            if patient_banner:
                content_controls.append(
                    ft.Container(
                        padding=10,
                        bgcolor="#F0FDFA",
                        content=ft.Text(f"Current Patient: {patient_banner[0]['first_name']} {patient_banner[0]['last_name']}")
                    )
                )

            vitals = get_query_data("""
                SELECT
                    temperature, blood_pressure, pulse_rate, respiratory_rate,
                    oxygen_saturation, weight, height, blood_sugar, notes, recorded_at
                FROM VitalSigns
                WHERE patient_id=%s
                ORDER BY recorded_at DESC
            """, (pid,))

            history = get_query_data("""
                SELECT condition_name, diagnosed_date, status, notes
                FROM MedicalHistory
                WHERE patient_id=%s
                ORDER BY diagnosed_date DESC
            """, (pid,))

            allergies = get_query_data("SELECT allergen FROM Allergy WHERE patient_id=%s", (pid,))

            vitals_widgets = []
            if vitals:
                for v in vitals:
                    vitals_widgets.append(
                        ft.Container(
                            padding=10,
                            border_radius=8,
                            bgcolor=ft.Colors.GREY_100,
                            content=ft.Column([
                                ft.Text(f"Temp: {v.get('temperature')} | BP: {v.get('blood_pressure')} | Pulse: {v.get('pulse_rate')}"),
                                ft.Text(f"Resp: {v.get('respiratory_rate')} | SpO2: {v.get('oxygen_saturation')} | Weight: {v.get('weight')} | Height: {v.get('height')}"),
                                ft.Text(f"Blood Sugar: {v.get('blood_sugar')} | {v.get('recorded_at')}"),
                                ft.Text(f"Notes: {v.get('notes') or 'N/A'}")
                            ])
                        )
                    )
            else:
                vitals_widgets.append(ft.Text("No vitals recorded"))

            history_widgets = []
            if history:
                for h in history:
                    history_widgets.append(
                        ft.Container(
                            padding=10,
                            border_radius=8,
                            bgcolor="#F0FDFA",
                            content=ft.Column([
                                ft.Text(f"{h.get('condition_name')} | {h.get('status')}"),
                                ft.Text(f"Diagnosed: {h.get('diagnosed_date')}"),
                                ft.Text(f"Notes: {h.get('notes') or 'N/A'}")
                            ])
                        )
                    )
            else:
                history_widgets.append(ft.Text("No medical history available"))

            allergy_widgets = []
            if allergies:
                for a in allergies:
                    allergy_widgets.append(ft.Text(a.get('allergen')))
            else:
                allergy_widgets.append(ft.Text("No allergies recorded"))

            content_controls.append(
                ft.Column([
                    ft.Text(f"{p['first_name']} {p['last_name']}", size=24, weight="bold"),
                    ft.Text(f"Blood Group: {p['blood_group']} | Phone: {p['phone']}"),
                    ft.Text(f"Address: {p['address']}"),
                ])
            )

            content_controls.append(
                ft.Container(
                    padding=10,
                    content=ft.Column([
                        ft.Text("Vitals", size=18, weight="bold"),
                        *vitals_widgets
                    ])
                )
            )

            content_controls.append(
                ft.Container(
                    padding=10,
                    content=ft.Column([
                        ft.Text("Medical History", size=18, weight="bold"),
                        *history_widgets
                    ])
                )
            )

            content_controls.append(
                ft.Container(
                    padding=10,
                    content=ft.Column([
                        ft.Text("Allergies", size=18, weight="bold"),
                        *allergy_widgets
                    ])
                )
            )

            condition_name = ft.TextField(label="Condition Name")
            diagnosed_date = ft.TextField(label="Diagnosed Date (YYYY-MM-DD)")
            hist_status = ft.Dropdown(
                label="Status",
                options=[
                    ft.dropdown.Option("Active"),
                    ft.dropdown.Option("Resolved"),
                    ft.dropdown.Option("Chronic")
                ]
            )
            hist_notes = ft.TextField(label="Notes")

            def save_history(e):
                if not page.session.store.get("selected_patient_id"):
                    show_snack("Select patient first", ft.Colors.RED)
                    return

                execute_query("""
                    INSERT INTO MedicalHistory
                    (patient_id, condition_name, diagnosed_date, status, notes)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    page.session.store.get("selected_patient_id"),
                    condition_name.value,
                    diagnosed_date.value,
                    hist_status.value,
                    hist_notes.value
                ))

                show_snack("Medical History Added", ft.Colors.GREEN)
                nav_to("doctor_patient")

            content_controls.append(
                ft.Container(
                    padding=10,
                    content=ft.Column([
                        ft.Text("Add Medical History", weight="bold"),
                        condition_name,
                        diagnosed_date,
                        hist_status,
                        hist_notes,
                        ft.FilledButton("Save", on_click=save_history, bgcolor="#0F766E", color="white")
                    ])
                )
            )

            temp = ft.TextField(label="Temperature")
            bp = ft.TextField(label="Blood Pressure")
            pulse = ft.TextField(label="Pulse Rate")
            resp = ft.TextField(label="Respiratory Rate")
            spo2 = ft.TextField(label="Oxygen Saturation")
            weight = ft.TextField(label="Weight")
            height = ft.TextField(label="Height")
            sugar = ft.TextField(label="Blood Sugar")
            vitals_notes = ft.TextField(label="Notes")

            def save_vitals(e):
                pid_local = page.session.store.get("selected_patient_id")
                doc_id = page.session.store.get("doctor_id")

                execute_query("""
                    INSERT INTO VitalSigns
                    (patient_id, recorded_by, temperature, blood_pressure, pulse_rate,
                    respiratory_rate, oxygen_saturation, weight, height, blood_sugar, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    pid_local, doc_id,
                    temp.value, bp.value, pulse.value,
                    resp.value, spo2.value,
                    weight.value, height.value,
                    sugar.value, vitals_notes.value
                ))

                show_snack("Vitals Saved", ft.Colors.GREEN)
                nav_to("doctor_patient")

            content_controls.append(
                ft.Container(
                    padding=10,
                    content=ft.Column([
                        ft.Text("Add Vitals", size=18, weight="bold"),
                        temp,
                        bp,
                        pulse,
                        resp,
                        spo2,
                        weight,
                        height,
                        sugar,
                        vitals_notes,
                        ft.FilledButton("Save Vitals", on_click=save_vitals, bgcolor="#0F766E", color="white")
                    ])
                )
            )
            
        elif tab == "doctor_prescription":
            pid = page.session.store.get("selected_patient_id")
            # 🔹 FETCH PRESCRIPTIONS
            prescriptions = get_query_data("""
                SELECT 
                    p.prescription_id,
                    m.medicine_name,
                    pi.dosage,
                    pi.frequency,
                    pi.duration_days,
                    p.prescribed_at
                FROM Prescription p
                JOIN PrescriptionItem pi ON p.prescription_id = pi.prescription_id
                JOIN Medicine m ON pi.medicine_id = m.medicine_id
                WHERE p.patient_id = %s
                ORDER BY p.prescribed_at DESC
            """, (pid,))

            # 🔹 Patient Banner
            if pid:
                patient_data = get_query_data(
                    "SELECT first_name, last_name FROM Patient WHERE patient_id=%s",
                    (pid,)
                )
                if patient_data:
                    content_controls.append(
                        ft.Container(
                            padding=10,
                            bgcolor="#F0FDFA",
                            content=ft.Text(
                                f"Current Patient: {patient_data[0]['first_name']} {patient_data[0]['last_name']}"
                            )
                        )
                    )

            # 🔹 Prepare prescription list safely
            prescription_widgets = []

            if prescriptions:
                for item in prescriptions:
                    prescription_widgets.append(
                        ft.Text(
                            f"{item['medicine_name']} | {item['dosage']} | {item['frequency']} | {item['duration_days']} days\n 📅Prescribed on: {item['prescribed_at']}"
                        )
                    )
            else:
                prescription_widgets.append(
                    ft.Text("No prescriptions found")
                )

            # 🔹 Display UI
            content_controls.append(
                ft.Container(
                    padding=10,
                    content=ft.Column([
                        ft.Text("Previous Prescriptions", size=18, weight="bold"),
                        *prescription_widgets
                    ])
                )
            )        

            meds = get_query_data("SELECT medicine_id, medicine_name FROM Medicine")
            print(meds)
            if not meds:
                content_controls.append(ft.Text("No medicines available"))

            med_dropdown = ft.Dropdown(
                label="Select Medicine",
                options=[ft.dropdown.Option(key=str(m['medicine_id']), text=m['medicine_name']) for m in meds]
            )

            dose = ft.TextField(label="Dosage")
            freq = ft.TextField(label="Frequency (e.g. 2 times/day)")   # ✅ NEW
            duration = ft.TextField(label="Duration (days)")            # renamed meaning

            def prescribe(e):
                pid = page.session.store.get("selected_patient_id")
                doc_id = page.session.store.get("doctor_id")

                if not pid:
                    show_snack("Select patient first", ft.Colors.RED)
                    return

                conn = get_db_connection()
                cursor = conn.cursor()

                # 🔹 create prescription (with notes + valid_till)
                cursor.execute("""
                    INSERT INTO Prescription (patient_id, doctor_id, notes, valid_till)
                    VALUES (%s, %s, %s, %s)
                """, (
                    pid,
                    doc_id,
                    "General prescription",   # you can later make TextField
                    None
                ))

                pres_id = cursor.lastrowid

                # 🔹 add medicine item
                cursor.execute("""
                    INSERT INTO PrescriptionItem 
                    (prescription_id, medicine_id, dosage, frequency, duration_days)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    pres_id,
                    med_dropdown.value,
                    dose.value,
                    freq.value,
                    duration.value
                ))

                conn.commit()
                cursor.close()
                conn.close()

                show_snack("Prescription Added", ft.Colors.GREEN)
                nav_to("doctor_prescription")   # 🔥 refresh   # 🔥 refresh

            content_controls.append(
                ft.Container(
                    expand=True,
                    padding=20,
                    content=ft.Column(
                        spacing=15,
                        controls=[
                            ft.Text("Prescription Panel", size=20, weight="bold"),

                            med_dropdown,
                            dose,
                            freq,
                            duration,

                            ft.FilledButton("Add Prescription", bgcolor="#0F766E", color="white", on_click=prescribe)
                        ]
                    )
                )
            )
                   
        elif tab == "doctor_lab":

            rows = get_query_data("""
                SELECT 
                    lo.order_id,
                    p.first_name,
                    p.last_name,
                    lo.ordered_at,
                    lo.status
                FROM LabOrder lo
                JOIN Patient p ON lo.patient_id = p.patient_id
                ORDER BY lo.order_id DESC
            """)

            content_controls.append(ft.Text("Lab Orders", size=22, weight="bold"))

            if not rows:
                content_controls.append(ft.Text("No lab orders found"))
            else:
                for r in rows:
                    content_controls.append(
                        ft.Container(
                            padding=12,
                            margin=ft.Margin.only(bottom=10),
                            border_radius=10,
                            bgcolor="#F0FDFA",
                            content=ft.Column([
                                ft.Text(f"Order #{r['order_id']} - {r['first_name']} {r['last_name']}", weight="bold"),
                                ft.Text(f"Date: {r['ordered_at']}", size=12),
                                ft.Text(f"Status: {r['status']}")
                            ])
                        )
                    )
       
        elif tab == "lab_dashboard":
            lab_tech_id = page.session.store.get("lab_tech_id")

            if not lab_tech_id:
                content_controls.append(ft.Text("Lab technician session missing. Please log in again."))
                return

            tests_count = get_query_data("SELECT COUNT(*) AS c FROM LabTest")
            orders_count = get_query_data("SELECT COUNT(*) AS c FROM LabOrder")
            pending_count = get_query_data("SELECT COUNT(*) AS c FROM LabOrder WHERE status != 'Completed'")
            results_count = get_query_data("SELECT COUNT(*) AS c FROM LabResult")

            total_tests = tests_count[0]["c"] if tests_count else 0
            total_orders = orders_count[0]["c"] if orders_count else 0
            pending_orders = pending_count[0]["c"] if pending_count else 0
            total_results = results_count[0]["c"] if results_count else 0

            content_controls.append(
                ft.Container(
                    margin=ft.Margin.only(bottom=12),
                    padding=16,
                    border_radius=12,
                    bgcolor="#F0FDFA",
                    content=ft.Column([
                        ft.Text("Lab Technician Dashboard", size=24, weight="bold"),
                        ft.Text("Tests, orders, results, and history in one workspace."),
                        ft.Row(
                            controls=[
                                ft.Container(
                                    padding=12,
                                    border_radius=10,
                                    bgcolor=ft.Colors.WHITE,
                                    width=170,
                                    content=ft.Column([
                                        ft.Text("Tests", size=12, color=ft.Colors.GREY_600),
                                        ft.Text(str(total_tests), size=22, weight="bold")
                                    ])
                                ),
                                ft.Container(
                                    padding=12,
                                    border_radius=10,
                                    bgcolor=ft.Colors.WHITE,
                                    width=170,
                                    content=ft.Column([
                                        ft.Text("Orders", size=12, color=ft.Colors.GREY_600),
                                        ft.Text(str(total_orders), size=22, weight="bold")
                                    ])
                                ),
                                ft.Container(
                                    padding=12,
                                    border_radius=10,
                                    bgcolor=ft.Colors.WHITE,
                                    width=170,
                                    content=ft.Column([
                                        ft.Text("Pending", size=12, color=ft.Colors.GREY_600),
                                        ft.Text(str(pending_orders), size=22, weight="bold")
                                    ])
                                ),
                                ft.Container(
                                    padding=12,
                                    border_radius=10,
                                    bgcolor=ft.Colors.WHITE,
                                    width=170,
                                    content=ft.Column([
                                        ft.Text("Results", size=12, color=ft.Colors.GREY_600),
                                        ft.Text(str(total_results), size=22, weight="bold")
                                    ])
                                ),
                            ],
                            spacing=12,
                        )
                    ])
                )
            )

            content_controls.append(
                ft.Row(
                    controls=[
                        ft.FilledButton("Test Catalog", bgcolor="#0F766E", color=ft.Colors.WHITE, on_click=lambda e: nav_to("lab_catalog")),
                        ft.FilledButton("Lab Orders", bgcolor="#0F766E", color=ft.Colors.WHITE, on_click=lambda e: nav_to("lab_orders")),
                        ft.FilledButton("Enter Result", bgcolor="#0F766E", color=ft.Colors.WHITE, on_click=lambda e: nav_to("lab_enter_result")),
                        ft.FilledButton("Result History", bgcolor="#0F766E", color=ft.Colors.WHITE, on_click=lambda e: nav_to("lab_history")),
                    ],
                    spacing=12
                )
            )  

        elif tab == "lab_catalog":
            tests_catalog = get_query_data("""
                SELECT
                    t.test_id,
                    t.test_name,
                    t.test_code,
                    COALESCE(c.category_name, 'Uncategorized') AS category_name,
                    t.description,
                    t.sample_type,
                    t.sample_volume,
                    t.normal_range,
                    t.unit,
                    t.turnaround_hours,
                    t.price,
                    t.equipment_required
                FROM LabTest t
                LEFT JOIN LabTestCategory c ON t.test_cat_id = c.test_cat_id
                ORDER BY category_name, t.test_name
            """)

            test_groups = {}
            for t in tests_catalog or []:
                cat = t.get("category_name") or "Uncategorized"
                test_groups.setdefault(cat, []).append(t)

            content_controls.append(ft.Text("Test Categories & Catalog", size=20, weight="bold"))

            if test_groups:
                for cat_name, items in test_groups.items():
                    item_cards = []
                    for t in items:
                        item_cards.append(
                            ft.Container(
                                margin=ft.Margin.only(bottom=8),
                                padding=12,
                                border_radius=10,
                                bgcolor="#F0FDFA",
                                content=ft.Column([
                                    ft.Text(f"{t['test_name']} ({t.get('test_code') or 'No code'})", weight="bold"),
                                    ft.Text(f"Sample: {t.get('sample_type') or 'N/A'} | Volume: {t.get('sample_volume') or 'N/A'}"),
                                    ft.Text(f"Range: {t.get('normal_range') or 'N/A'} | Unit: {t.get('unit') or 'N/A'}"),
                                    ft.Text(f"Turnaround: {t.get('turnaround_hours') or 'N/A'} hrs | Price: {t.get('price') or 'N/A'}"),
                                    ft.Text(f"Equipment: {t.get('equipment_required') or 'N/A'}"),
                                    ft.Text(f"Description: {t.get('description') or 'N/A'}"),
                                ])
                            )
                        )

                    content_controls.append(
                        ft.Container(
                            margin=ft.Margin.only(bottom=12),
                            padding=14,
                            border_radius=12,
                            bgcolor=ft.Colors.WHITE,
                            content=ft.Column([
                                ft.Text(cat_name, size=16, weight="bold"),
                                *item_cards
                            ])
                        )
                    )
            else:
                content_controls.append(ft.Text("No lab tests found"))  

        elif tab == "lab_orders":
            lab_orders = get_query_data("""
                SELECT
                    lo.order_id,
                    loi.order_item_id,
                    p.first_name AS patient_first,
                    p.last_name AS patient_last,
                    d.first_name AS doctor_first,
                    d.last_name AS doctor_last,
                    t.test_name,
                    t.test_code,
                    COALESCE(c.category_name, 'Uncategorized') AS category_name,
                    t.sample_type,
                    t.sample_volume,
                    t.normal_range,
                    t.unit,
                    t.turnaround_hours,
                    t.price,
                    t.equipment_required,
                    lo.priority,
                    lo.status,
                    lo.ordered_at,
                    lo.notes
                FROM LabOrder lo
                JOIN LabOrderItem loi ON lo.order_id = loi.order_id
                JOIN LabTest t ON loi.test_id = t.test_id
                LEFT JOIN LabTestCategory c ON t.test_cat_id = c.test_cat_id
                JOIN Patient p ON lo.patient_id = p.patient_id
                JOIN Doctor d ON lo.doctor_id = d.doctor_id
                ORDER BY lo.ordered_at DESC
            """)

            content_controls.append(ft.Text("Active Lab Orders", size=20, weight="bold"))

            if lab_orders:
                for o in lab_orders:
                    status_dd = ft.Dropdown(
                        width=220,
                        label="Update Status",
                        value=o["status"],
                        options=[
                            ft.dropdown.Option("Ordered"),
                            ft.dropdown.Option("Sample Collected"),
                            ft.dropdown.Option("Processing"),
                            ft.dropdown.Option("Completed"),
                            ft.dropdown.Option("Cancelled"),
                        ]
                    )

                    content_controls.append(
                        ft.Container(
                            margin=ft.Margin.only(bottom=12),
                            padding=14,
                            border_radius=12,
                            bgcolor=ft.Colors.WHITE,
                            content=ft.Column([
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(f"{o['patient_first']} {o['patient_last']}", size=16, weight="bold"),
                                        ft.Container(
                                            padding=6,
                                            border_radius=8,
                                            bgcolor=priority_bg(o["priority"]),
                                            content=ft.Text(o["priority"], color=ft.Colors.WHITE, weight="bold")
                                        )
                                    ]
                                ),
                                ft.Text(f"Order ID: {o['order_id']} | Item ID: {o['order_item_id']}"),
                                ft.Text(f"Doctor: Dr. {o['doctor_first']} {o['doctor_last']}"),
                                ft.Text(f"Test: {o['test_name']} ({o.get('test_code') or 'No code'})"),
                                ft.Text(f"Category: {o.get('category_name') or 'Uncategorized'}"),
                                ft.Text(f"Sample: {o.get('sample_type') or 'N/A'} | Volume: {o.get('sample_volume') or 'N/A'}"),
                                ft.Text(f"Normal Range: {o.get('normal_range') or 'N/A'} | Unit: {o.get('unit') or 'N/A'}"),
                                ft.Text(f"Turnaround: {o.get('turnaround_hours') or 'N/A'} hrs | Price: {o.get('price') or 'N/A'}"),
                                ft.Text(f"Ordered At: {fmt_dt(o.get('ordered_at'))}"),
                                ft.Text(f"Notes: {o.get('notes') or 'N/A'}"),
                                ft.Row(
                                    controls=[
                                        ft.Container(
                                            padding=6,
                                            border_radius=8,
                                            bgcolor=status_bg(o["status"]),
                                            content=ft.Text(o["status"], color=ft.Colors.WHITE, weight="bold")
                                        ),
                                        status_dd,
                                        ft.FilledButton(
                                            "Save Status",
                                            bgcolor="#0F766E", color=ft.Colors.WHITE,
                                            on_click=lambda e, oid=o["order_id"], dd=status_dd: update_order_status(oid, dd.value)
                                        )
                                    ],
                                    spacing=12
                                )
                            ])
                        )
                    )
            else:
                content_controls.append(ft.Text("No lab orders found"))   

        elif tab == "lab_enter_result":
            pending_items = get_query_data("""
                SELECT
                    loi.order_item_id,
                    lo.order_id,
                    p.first_name,
                    p.last_name,
                    t.test_name,
                    lo.ordered_at
                FROM LabOrderItem loi
                JOIN LabOrder lo ON loi.order_id = lo.order_id
                JOIN Patient p ON lo.patient_id = p.patient_id
                JOIN LabTest t ON loi.test_id = t.test_id
                WHERE lo.status IN ('Ordered', 'Sample Collected', 'Processing')
                ORDER BY lo.ordered_at DESC
            """)

            doctors = get_query_data("""
                SELECT doctor_id, first_name, last_name
                FROM Doctor
                ORDER BY first_name, last_name
            """)

            item_dropdown = ft.Dropdown(
                label="Select Order Item",
                width=420,
                options=[
                    ft.dropdown.Option(
                        key=str(i["order_item_id"]),
                        text=f"#{i['order_item_id']} | {i['first_name']} {i['last_name']} | {i['test_name']} | {fmt_dt(i.get('ordered_at'))}"
                    )
                    for i in (pending_items or [])
                ]
            )

            result_value = ft.TextField(label="Result Value", width=300)
            result_unit = ft.TextField(label="Unit", width=180)
            result_normal_range = ft.TextField(label="Normal Range", width=240)
            result_status = ft.Dropdown(
                label="Result Status",
                width=220,
                options=[
                    ft.dropdown.Option("Normal"),
                    ft.dropdown.Option("Abnormal"),
                    ft.dropdown.Option("Critical"),
                ],
                value="Normal"
            )
            result_remarks = ft.TextField(label="Remarks", multiline=True, min_lines=2, max_lines=4, width=520)

            verified_by = ft.Dropdown(
                label="Verified By Doctor (optional)",
                width=320,
                options=[ft.dropdown.Option("None")] + [
                    ft.dropdown.Option(
                        key=str(d["doctor_id"]),
                        text=f"Dr. {d['first_name']} {d['last_name']}"
                    )
                    for d in (doctors or [])
                ],
                value="None"
            )

            def submit_result(e):
                if not item_dropdown.value:
                    show_snack("Select an order item first.", ft.Colors.RED)
                    return

                conn = get_db_connection()
                if not conn:
                    return

                cursor = conn.cursor()
                try:
                    verified_value = None
                    if verified_by.value and verified_by.value != "None":
                        verified_value = int(verified_by.value)

                    cursor.execute("""
                        INSERT INTO LabResult (
                            order_item_id,
                            lab_tech_id,
                            sample_collected_at,
                            result_value,
                            unit,
                            normal_range,
                            status,
                            remarks,
                            verified_by
                        )
                        VALUES (%s, %s, NOW(), %s, %s, %s, %s, %s, %s)
                    """, (
                        int(item_dropdown.value),
                        int(lab_tech_id),
                        result_value.value,
                        result_unit.value,
                        result_normal_range.value,
                        result_status.value,
                        result_remarks.value,
                        verified_value
                    ))

                    cursor.execute("""
                        SELECT order_id
                        FROM LabOrderItem
                        WHERE order_item_id = %s
                    """, (int(item_dropdown.value),))
                    row = cursor.fetchone()
                    if row:
                        cursor.execute("""
                            UPDATE LabOrder
                            SET status='Completed'
                            WHERE order_id=%s
                        """, (row[0],))

                    conn.commit()
                    show_snack("Lab result submitted.", ft.Colors.GREEN)
                    nav_to("lab_history")
                except Exception as ex:
                    conn.rollback()
                    show_snack(f"Lab result error: {ex}", ft.Colors.RED)
                finally:
                    cursor.close()
                    conn.close()

            content_controls.append(ft.Text("Enter Lab Result", size=20, weight="bold"))
            content_controls.append(
                ft.Container(
                    padding=14,
                    border_radius=12,
                    bgcolor=ft.Colors.WHITE,
                    content=ft.Column([
                        item_dropdown,
                        ft.Row([result_value, result_unit, result_normal_range], spacing=12),
                        ft.Row([result_status, verified_by], spacing=12),
                        result_remarks,
                        ft.FilledButton("Submit Lab Result", bgcolor="#0F766E", color=ft.Colors.WHITE, on_click=submit_result)
                    ], spacing=12)
                )
            ) 

        elif tab == "lab_history":
            results = get_query_data("""
                SELECT
                    lr.result_id,
                    p.first_name AS patient_first,
                    p.last_name AS patient_last,
                    t.test_name,
                    lr.result_value,
                    lr.unit,
                    lr.normal_range,
                    lr.status,
                    lr.remarks,
                    lr.sample_collected_at,
                    lr.reported_at,
                    d1.first_name AS verifier_first,
                    d1.last_name AS verifier_last
                FROM LabResult lr
                JOIN LabOrderItem loi ON lr.order_item_id = loi.order_item_id
                JOIN LabOrder lo ON loi.order_id = lo.order_id
                JOIN Patient p ON lo.patient_id = p.patient_id
                JOIN LabTest t ON loi.test_id = t.test_id
                LEFT JOIN Doctor d1 ON lr.verified_by = d1.doctor_id
                ORDER BY lr.reported_at DESC
            """)

            content_controls.append(ft.Text("Results History", size=20, weight="bold"))

            result_cards = []
            if results:
                for r in results:
                    verifier_name = "N/A"
                    if r.get("verifier_first"):
                        verifier_name = f"Dr. {r['verifier_first']} {r['verifier_last']}"

                    result_cards.append(
                        ft.Container(
                            margin=ft.Margin.only(bottom=12),
                            padding=14,
                            border_radius=12,
                            bgcolor=ft.Colors.GREY_100,
                            content=ft.Column([
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(f"{r['patient_first']} {r['patient_last']}", weight="bold"),
                                        ft.Container(
                                            padding=6,
                                            border_radius=8,
                                            bgcolor=status_bg(r["status"]),
                                            content=ft.Text(r["status"], color=ft.Colors.WHITE, weight="bold")
                                        )
                                    ]
                                ),
                                ft.Text(f"Test: {r['test_name']}"),
                                ft.Text(f"Result: {r['result_value']} {r.get('unit') or ''}"),
                                ft.Text(f"Normal Range: {r.get('normal_range') or 'N/A'}"),
                                ft.Text(f"Sample Collected: {fmt_dt(r.get('sample_collected_at'))}"),
                                ft.Text(f"Reported: {fmt_dt(r.get('reported_at'))}"),
                                ft.Text(f"Verified By: {verifier_name}"),
                                ft.Text(f"Remarks: {r.get('remarks') or 'N/A'}"),
                            ])
                        )
                    )
            else:
                result_cards.append(ft.Text("No results available"))

            content_controls.append(
                ft.Column(result_cards, spacing=0)
            )  
        elif tab == "pharma_dashboard":
            meds = get_query_data("SELECT COUNT(*) AS c FROM Medicine")
            low_stock = get_query_data("SELECT COUNT(*) AS c FROM Medicine WHERE stock_quantity <= reorder_level")
            expiring = get_query_data("SELECT COUNT(*) AS c FROM Medicine WHERE expiry_date <= DATE_ADD(CURDATE(), INTERVAL 90 DAY)")
            prescriptions = get_query_data("SELECT COUNT(*) AS c FROM Prescription")
            dispenses = get_query_data("SELECT COUNT(*) AS c FROM PharmacyDispense")
            invoices = get_query_data("SELECT COUNT(*) AS c FROM Invoice")

            total_meds = meds[0]["c"] if meds else 0
            low_stock_count = low_stock[0]["c"] if low_stock else 0
            expiring_count = expiring[0]["c"] if expiring else 0
            total_prescriptions = prescriptions[0]["c"] if prescriptions else 0
            total_dispenses = dispenses[0]["c"] if dispenses else 0
            total_invoices = invoices[0]["c"] if invoices else 0

            content_controls.append(
                ft.Container(
                    padding=16,
                    border_radius=12,
                    bgcolor="#F0FDFA",
                    content=ft.Column([
                        ft.Text("Pharmacy Dashboard", size=24, weight="bold"),
                        ft.Text("Inventory, prescriptions, dispensing, invoices, and sales in one place."),
                        ft.Row(
                            controls=[
                                ft.Container(
                                    padding=12,
                                    border_radius=10,
                                    bgcolor=ft.Colors.WHITE,
                                    width=170,
                                    content=ft.Column([
                                        ft.Text("Medicines", size=12, color=ft.Colors.GREY_600),
                                        ft.Text(str(total_meds), size=22, weight="bold")
                                    ])
                                ),
                                ft.Container(
                                    padding=12,
                                    border_radius=10,
                                    bgcolor=ft.Colors.WHITE,
                                    width=170,
                                    content=ft.Column([
                                        ft.Text("Low Stock", size=12, color=ft.Colors.GREY_600),
                                        ft.Text(str(low_stock_count), size=22, weight="bold")
                                    ])
                                ),
                                ft.Container(
                                    padding=12,
                                    border_radius=10,
                                    bgcolor=ft.Colors.WHITE,
                                    width=170,
                                    content=ft.Column([
                                        ft.Text("Expiring", size=12, color=ft.Colors.GREY_600),
                                        ft.Text(str(expiring_count), size=22, weight="bold")
                                    ])
                                ),
                                ft.Container(
                                    padding=12,
                                    border_radius=10,
                                    bgcolor=ft.Colors.WHITE,
                                    width=170,
                                    content=ft.Column([
                                        ft.Text("Prescriptions", size=12, color=ft.Colors.GREY_600),
                                        ft.Text(str(total_prescriptions), size=22, weight="bold")
                                    ])
                                ),
                                ft.Container(
                                    padding=12,
                                    border_radius=10,
                                    bgcolor=ft.Colors.WHITE,
                                    width=170,
                                    content=ft.Column([
                                        ft.Text("Dispenses", size=12, color=ft.Colors.GREY_600),
                                        ft.Text(str(total_dispenses), size=22, weight="bold")
                                    ])
                                ),
                                ft.Container(
                                    padding=12,
                                    border_radius=10,
                                    bgcolor=ft.Colors.WHITE,
                                    width=170,
                                    content=ft.Column([
                                        ft.Text("Invoices", size=12, color=ft.Colors.GREY_600),
                                        ft.Text(str(total_invoices), size=22, weight="bold")
                                    ])
                                ),
                            ],
                            spacing=10
                        )
                    ])
                )
            )

            content_controls.append(
                ft.Row(
                    controls=[
                        ft.FilledButton("Inventory", bgcolor="#0F766E", color=ft.Colors.WHITE, on_click=lambda e: nav_to("pharma_inventory")),
                        ft.FilledButton("Prescriptions", bgcolor="#0F766E", color=ft.Colors.WHITE, on_click=lambda e: nav_to("pharma_prescriptions")),
                        ft.FilledButton("Dispense", bgcolor="#0F766E", color=ft.Colors.WHITE, on_click=lambda e: nav_to("pharma_dispense")),
                        ft.FilledButton("Invoices", bgcolor="#0F766E", color=ft.Colors.WHITE, on_click=lambda e: nav_to("pharma_invoice")),
                        ft.FilledButton("Sales", bgcolor="#0F766E", color=ft.Colors.WHITE, on_click=lambda e: nav_to("pharma_sales")),
                    ],
                    spacing=12
                )
            )                 
        elif tab == "pharma_inventory":
            meds, groups = get_medicine_category_groups()

            content_controls.append(ft.Text("Medicine Inventory", size=20, weight="bold"))

            if not groups:
                content_controls.append(ft.Text("No medicines found"))
            else:
                for cat_name, items in groups.items():
                    cards = []
                    for m in items:
                        stock_status = "Low Stock" if m["stock_quantity"] <= m["reorder_level"] else "In Stock"
                        expiry_text = fmt_dt(m.get("expiry_date"))
                        cards.append(
                            ft.Container(
                                padding=12,
                                margin=ft.Margin.only(bottom=8),
                                border_radius=10,
                                bgcolor=ft.Colors.GREY_100,
                                content=ft.Column([
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.Text(m["medicine_name"], weight="bold"),
                                            ft.Container(
                                                padding=6,
                                                border_radius=8,
                                                bgcolor=ft.Colors.RED_400 if stock_status == "Low Stock" else ft.Colors.GREEN_500,
                                                content=ft.Text(stock_status, color=ft.Colors.WHITE, weight="bold")
                                            )
                                        ]
                                    ),
                                    ft.Text(f"Generic: {m.get('generic_name') or 'N/A'} | Brand: {m.get('brand_name') or 'N/A'}"),
                                    ft.Text(f"Form: {m.get('dosage_form') or 'N/A'} | Strength: {m.get('strength') or 'N/A'}"),
                                    ft.Text(f"Category: {cat_name} | Unit Price: ₹{m.get('unit_price')}"),
                                    ft.Text(f"Stock: {m.get('stock_quantity')} | Reorder Level: {m.get('reorder_level')}"),
                                    ft.Text(f"Expiry: {expiry_text} | Storage: {m.get('storage_condition') or 'N/A'}"),
                                    ft.Text(f"Prescription Required: {'Yes' if m.get('prescription_required') else 'No'}"),
                                ])
                            )
                        )

                    content_controls.append(
                        ft.Container(
                            padding=14,
                            margin=ft.Margin.only(bottom=12),
                            border_radius=12,
                            bgcolor=ft.Colors.WHITE,
                            content=ft.Column([
                                ft.Text(cat_name, size=16, weight="bold"),
                                *cards
                            ])
                        )
                    )
        
        elif tab == "pharma_sales":

    # 🔹 FETCH ONLY PHARMACY INVOICES
            invoices = get_query_data("""
                SELECT *
                FROM Invoice
                WHERE bill_type = 'PHARMACY'
                ORDER BY invoice_date DESC
            """)

            # 🔹 TOTAL PAID
            total_sales = get_query_data("""
                SELECT COALESCE(SUM(total_amount), 0) AS s
                FROM Invoice
                WHERE bill_type = 'PHARMACY'
                AND payment_status = 'Paid'
            """)

            # 🔹 TOTAL DUE
            total_due = get_query_data("""
                SELECT COALESCE(SUM(due_amount), 0) AS s
                FROM Invoice
                WHERE bill_type = 'PHARMACY'
                AND payment_status != 'Paid'
            """)

            sales_value = total_sales[0]["s"] if total_sales else 0
            due_value = total_due[0]["s"] if total_due else 0

            content_controls.append(ft.Text("Pharmacy Sales", size=22, weight="bold"))

            content_controls.append(
                ft.Row([
                    ft.Container(
                        padding=12,
                        border_radius=10,
                        bgcolor=ft.Colors.GREEN_100,
                        content=ft.Text(f"Total Paid Sales: ₹{sales_value}", weight="bold")
                    ),
                    ft.Container(
                        padding=12,
                        border_radius=10,
                        bgcolor=ft.Colors.RED_100,
                        content=ft.Text(f"Pending Due: ₹{due_value}", weight="bold")
                    )
                ], spacing=12)
            )

            if invoices:
                for inv in invoices:

                    mode_dd = ft.Dropdown(
                        width=150,
                        options=[
                            ft.dropdown.Option("Cash"),
                            ft.dropdown.Option("UPI"),
                            ft.dropdown.Option("Card"),
                            ft.dropdown.Option("Insurance"),
                        ],
                        value=inv.get("payment_mode") or "Cash"
                    )

                    content_controls.append(
                        ft.Container(
                            padding=12,
                            margin=ft.Margin.only(bottom=10),
                            bgcolor="#F0FDFA",
                            border_radius=10,
                            content=ft.Column([
                                ft.Text(f"{inv['invoice_number']}", weight="bold"),
                                ft.Text(f"Date: {fmt_dt(inv.get('invoice_date'))}"),
                                ft.Text(f"Total: ₹{inv['total_amount']} | Paid: ₹{inv['paid_amount']} | Due: ₹{inv['due_amount']}"),
                                ft.Text(f"Payment: {inv['payment_status']} | Mode: {inv.get('payment_mode') or 'N/A'}"),
                                ft.Text(f"Notes: {inv.get('notes') or 'N/A'}"),

                                ft.Row([
                                    mode_dd,
                                    ft.FilledButton(
                                        "Mark Paid",
                                        bgcolor="#0F766E", color=ft.Colors.WHITE,
                                        on_click=lambda e, iid=inv["invoice_id"], dd=mode_dd:
                                            mark_invoice_paid(iid, dd.value)
                                    )
                                ])
                            ])
                        )
                    )
            else:
                content_controls.append(ft.Text("No pharmacy invoices found"))
        elif tab == "pharma_invoice":

            pharmacist_id = page.session.store.get("pharmacist_id")
            if not pharmacist_id:
                content_controls.append(ft.Text("Pharmacist session missing. Please log in again."))
                return

            # =========================
            # LOAD DISPENSE LIST
            # =========================
            dispenses = get_query_data("""
                SELECT
                    pd.dispense_id,
                    p.first_name,
                    p.last_name,
                    pd.dispensed_at,
                    pd.payment_status
                FROM PharmacyDispense pd
                JOIN Patient p ON pd.patient_id = p.patient_id
                ORDER BY pd.dispensed_at DESC
            """)

            dispense_dd = ft.Dropdown(
                label="Select Dispense",
                width=420,
                options=[
                    ft.dropdown.Option(
                        key=str(d["dispense_id"]),
                        text=f"Dispense #{d['dispense_id']} | {d['first_name']} {d['last_name']} | {d['payment_status']}"
                    )
                    for d in (dispenses or [])
                ]
            )

            collect_now_sw = ft.Switch(label="Collect Payment Now", value=True, active_color="#0F766E")

            payment_mode_dd = ft.Dropdown(
                label="Payment Mode",
                width=220,
                options=[
                    ft.dropdown.Option("Cash"),
                    ft.dropdown.Option("UPI"),
                    ft.dropdown.Option("Card"),
                    ft.dropdown.Option("Insurance"),
                ],
                value="Cash"
            )

            preview = ft.Column(spacing=8)

            # =========================
            # LOAD PREVIEW
            # =========================
            def load_dispense_preview(e):

                preview.controls.clear()

                # 🔹 Check selection
                if not dispense_dd.value:
                    preview.controls.append(ft.Text("Select a dispense first"))
                    preview.update()
                    return

                did = int(dispense_dd.value)

                # 🔹 Fetch medicines
                lines = get_query_data("""
                    SELECT
                        di.quantity,
                        di.unit_price,
                        m.medicine_name
                    FROM DispenseItem di
                    JOIN Medicine m ON di.medicine_id = m.medicine_id
                    WHERE di.dispense_id = %s
                    ORDER BY di.dispense_item_id
                """, (did,))

                if not lines:
                    preview.controls.append(ft.Text("No dispense items found"))
                    preview.update()
                    return

                # 🔹 Calculate total
                total = 0

                for l in lines:
                    item_total = l["quantity"] * l["unit_price"]
                    total += item_total

                    preview.controls.append(
                        ft.Text(
                            f"{l['medicine_name']} | Qty: {l['quantity']} | ₹{l['unit_price']} | Total ₹{item_total}"
                        )
                    )

                preview.controls.append(
                    ft.Text(f"Grand Total: ₹{total}", weight="bold")
                )

                preview.update()

            # =========================
            # GENERATE INVOICE
            # =========================
            def generate_pharmacy_invoice(e):

                if not dispense_dd.value:
                    show_snack("Select dispense first", ft.Colors.RED)
                    return

                lines = get_query_data("""
                    SELECT di.quantity, di.unit_price, m.medicine_name
                    FROM DispenseItem di
                    JOIN Medicine m ON di.medicine_id = m.medicine_id
                    WHERE di.dispense_id = %s
                """, (dispense_dd.value,))
                
                row = get_query_data("""
                    SELECT patient_id
                    FROM PharmacyDispense
                    WHERE dispense_id = %s
                """, (dispense_dd.value,))

                if not row:
                    show_snack("Dispense not found", ft.Colors.RED)
                    return

                patient_id = row[0]["patient_id"]
                items = []
                total = 0

                for l in lines:
                    item_total = l["quantity"] * l["unit_price"]
                    total += item_total

                    items.append({
                        "item_type": "Medicine",
                        "description": l["medicine_name"],
                        "quantity": int(l["quantity"]),
                        "unit_price": float(l["unit_price"])
                    })

                # ✅ SAVE INVOICE
                invoice_id = save_invoice_record(
                patient_id=patient_id,
                bill_type="PHARMACY",   # ✅ HARD CODE THIS
                items=items,
                collect_now=collect_now_sw.value,
                payment_mode=payment_mode_dd.value,
                notes=f"Dispense {dispense_dd.value}",
                dispense_id=dispense_dd.value
                )

                print("INVOICE ID:", invoice_id)   # ✅ DEBUG
                if invoice_id:
                    show_snack("Invoice Created", ft.Colors.GREEN)
                    nav_to("pharma_sales")   # ✅ REFRESH SCREEN
                if invoice_id:
                    pdf_path = generate_invoice_pdf(invoice_id, items, total)
                    show_snack(f"PDF Saved: {pdf_path}", ft.Colors.GREEN)

                    import os
                    os.startfile(pdf_path)

            # =========================
            # UI
            # =========================
            content_controls.append(ft.Text("Pharmacy Invoice", size=24, weight="bold"))

            content_controls.append(
                ft.Container(
                    padding=16,
                    border_radius=12,
                    bgcolor=ft.Colors.WHITE,
                    content=ft.Column([
                        dispense_dd,
                        ft.Row([collect_now_sw, payment_mode_dd], spacing=12),
                        ft.Row([
                            ft.FilledButton("Load Preview", bgcolor="#0F766E", color=ft.Colors.WHITE, on_click=load_dispense_preview),
                            ft.FilledButton("Generate Invoice", bgcolor="#0F766E", color=ft.Colors.WHITE, on_click=generate_pharmacy_invoice)
                        ], spacing=12),
                        ft.Divider(),
                        ft.Text("Preview", weight="bold"),
                        preview
                    ], spacing=12)
                )
            )
        

        elif tab == "pharma_dispense":
            pharmacist_id = page.session.store.get("pharmacist_id")
            selected_prescription_id = page.session.store.get("selected_prescription_id")

            if not pharmacist_id:
                content_controls.append(ft.Text("Pharmacist session missing. Please log in again."))
                return

            prescriptions = get_query_data("""
                SELECT
                    p.prescription_id,
                    pt.first_name,
                    pt.last_name,
                    p.prescribed_at
                FROM Prescription p
                JOIN Patient pt ON p.patient_id = pt.patient_id
                ORDER BY p.prescribed_at DESC
            """)

            prescription_dd = ft.Dropdown(
                label="Select Prescription",
                width=420,
                value=str(selected_prescription_id) if selected_prescription_id else None,
                options=[
                    ft.dropdown.Option(
                        key=str(p["prescription_id"]),
                        text=f"#{p['prescription_id']} | {p['first_name']} {p['last_name']} | {fmt_dt(p.get('prescribed_at'))}"
                    )
                    for p in (prescriptions or [])
                ]
            )

            items_area = ft.Column(spacing=10)
            qty_inputs = []

            def load_items(e):
                qty_inputs.clear()
                items_area.controls.clear()

                if not prescription_dd.value:
                    items_area.controls.append(ft.Text("Select a prescription first"))
                    items_area.update()
                    return

                page.session.store.set("selected_prescription_id", prescription_dd.value)

                items = get_query_data("""
                    SELECT
                        pi.item_id,
                        pi.medicine_id,
                        m.medicine_name,
                        m.unit_price,
                        m.stock_quantity,
                        pi.dosage,
                        pi.frequency,
                        pi.duration_days
                    FROM PrescriptionItem pi
                    JOIN Medicine m ON pi.medicine_id = m.medicine_id
                    WHERE pi.prescription_id = %s
                    ORDER BY pi.item_id
                """, (prescription_dd.value,))

                if not items:
                    items_area.controls.append(ft.Text("No medicines found in this prescription"))
                    items_area.update()
                    return

                for it in items:
                    qty = ft.TextField(label="Qty", width=100, value="1")
                    qty_inputs.append((it, qty))
                    items_area.controls.append(
                        ft.Container(
                            padding=12,
                            border_radius=10,
                            bgcolor=ft.Colors.GREY_100,
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Column([
                                        ft.Text(it["medicine_name"], weight="bold"),
                                        ft.Text(f"Dosage: {it.get('dosage') or 'N/A'}"),
                                        ft.Text(f"Frequency: {it.get('frequency') or 'N/A'}"),
                                        ft.Text(f"Duration: {it.get('duration_days') or 'N/A'} days"),
                                        ft.Text(f"Unit Price: ₹{it.get('unit_price')}"),
                                        ft.Text(f"Stock Available: {it.get('stock_quantity')}"),
                                    ]),
                                    qty
                                ]
                            )
                        )
                    )

                items_area.update()

            def save_dispense(e):
                if not prescription_dd.value:
                    show_snack("Select a prescription first", ft.Colors.RED)
                    return

                if not qty_inputs:
                    show_snack("Load prescription items first", ft.Colors.RED)
                    return

                conn = get_db_connection()
                if not conn:
                    return

                cursor = conn.cursor()
                try:
                    cursor.execute(
                        "SELECT patient_id FROM Prescription WHERE prescription_id=%s",
                        (prescription_dd.value,)
                    )
                    p_row = cursor.fetchone()
                    if not p_row:
                        raise Exception("Prescription not found")

                    patient_id = p_row[0]
                    total_amount = 0.0

                    cursor.execute("""
                        INSERT INTO PharmacyDispense (
                            prescription_id, patient_id, pharmacist_id,
                            dispensed_at, total_amount, payment_status
                        )
                        VALUES (%s, %s, %s, NOW(), 0, 'Pending')
                    """, (prescription_dd.value, patient_id, pharmacist_id))

                    dispense_id = cursor.lastrowid

                    for it, qty_field in qty_inputs:
                        qty = int(qty_field.value or 0)
                        if qty <= 0:
                            continue

                        stock = int(it["stock_quantity"] or 0)
                        if qty > stock:
                            raise Exception(f"Insufficient stock for {it['medicine_name']}")

                        unit_price = float(it["unit_price"] or 0)
                        line_total = qty * unit_price
                        total_amount += line_total

                        cursor.execute("""
                            INSERT INTO DispenseItem (
                                dispense_id, medicine_id, quantity, unit_price, total_price
                            )
                            VALUES (%s, %s, %s, %s, %s)
                        """, (dispense_id, it["medicine_id"], qty, unit_price, line_total))

                        cursor.execute("""
                            UPDATE Medicine
                            SET stock_quantity = stock_quantity - %s
                            WHERE medicine_id = %s
                        """, (qty, it["medicine_id"]))

                    cursor.execute("""
                        UPDATE PharmacyDispense
                        SET total_amount = %s
                        WHERE dispense_id = %s
                    """, (total_amount, dispense_id))

                    conn.commit()
                    show_snack(f"Dispensed successfully. Total ₹{total_amount:.2f}", ft.Colors.GREEN)
                    nav_to("pharma_invoice")
                except Exception as ex:
                    conn.rollback()
                    show_snack(f"Dispense error: {ex}", ft.Colors.RED)
                finally:
                    cursor.close()
                    conn.close()

            content_controls.append(ft.Text("Dispense Medicines", size=20, weight="bold"))
            content_controls.append(
                ft.Container(
                    padding=14,
                    border_radius=12,
                    bgcolor=ft.Colors.WHITE,
                    content=ft.Column([
                        prescription_dd,
                        ft.Row([
                            ft.FilledButton("Load Prescription Items", bgcolor="#0F766E", color=ft.Colors.WHITE, on_click=load_items),
                            ft.FilledButton("Save Dispense", bgcolor="#0F766E", color=ft.Colors.WHITE, on_click=save_dispense)
                        ], spacing=12),
                        items_area
                    ], spacing=12)
                )
            )

        elif tab == "pharma_prescriptions":
            prescriptions = get_query_data("""
                SELECT
                    p.prescription_id,
                    p.prescribed_at,
                    p.valid_till,
                    p.notes,
                    pt.first_name,
                    pt.last_name,
                    d.first_name AS doctor_first,
                    d.last_name AS doctor_last
                FROM Prescription p
                JOIN Patient pt ON p.patient_id = pt.patient_id
                JOIN Doctor d ON p.doctor_id = d.doctor_id
                ORDER BY p.prescribed_at DESC
            """)

            content_controls.append(ft.Text("Doctor Prescriptions", size=20, weight="bold"))

            if not prescriptions:
                content_controls.append(ft.Text("No prescriptions found"))
            else:
                for p in prescriptions:
                    content_controls.append(
                        ft.Container(
                            margin=ft.Margin.only(bottom=12),
                            padding=14,
                            border_radius=12,
                            bgcolor="#F0FDFA",
                            content=ft.Column([
                                ft.Text(f"{p['first_name']} {p['last_name']}", size=16, weight="bold"),
                                ft.Text(f"Prescription ID: {p['prescription_id']}"),
                                ft.Text(f"Doctor: Dr. {p['doctor_first']} {p['doctor_last']}"),
                                ft.Text(f"Prescribed At: {fmt_dt(p.get('prescribed_at'))}"),
                                ft.Text(f"Valid Till: {fmt_dt(p.get('valid_till'))}"),
                                ft.Text(f"Notes: {p.get('notes') or 'N/A'}"),
                                ft.FilledButton(
                                    "Open in Dispense",
                                    bgcolor="#0F766E",
                                    color=ft.Colors.WHITE,
                                    on_click=lambda e, pid=p["prescription_id"]: (
                                        page.session.store.set("selected_prescription_id", pid),
                                        nav_to("pharma_dispense")
                                    )
                                )
                            ])
                        )
                    )
        elif tab == "billing":

            stats = get_query_data("""
                SELECT
                    COUNT(*) AS total_bills,
                    SUM(CASE WHEN payment_status = 'Paid' THEN 1 ELSE 0 END) AS paid_bills,
                    SUM(CASE WHEN payment_status != 'Paid' THEN 1 ELSE 0 END) AS unpaid_bills,
                    COALESCE(SUM(total_amount), 0) AS total_amount,
                    COALESCE(SUM(due_amount), 0) AS due_amount
                FROM Invoice
                WHERE bill_type IN ('OPD','LAB','IPD')
            """)

            s = stats[0] if stats else {}

            # 🔹 FETCH INVOICES
            invoices = get_query_data("""
                SELECT
                    i.invoice_id,
                    i.invoice_number,
                    i.bill_type,
                    i.invoice_date,
                    p.first_name,
                    p.last_name,
                    i.total_amount,
                    i.paid_amount,
                    i.due_amount,
                    i.payment_status,
                    i.payment_mode,
                    i.notes
                FROM Invoice i
                JOIN Patient p ON i.patient_id = p.patient_id
                WHERE i.bill_type IN ('OPD','LAB','IPD')   -- 🔥 IMPORTANT
                ORDER BY i.invoice_date DESC
            """)

            content_controls.append(ft.Text("Billing Overview", size=24, weight="bold"))

            # 🔹 SUMMARY
            content_controls.append(
                ft.Row([
                    ft.Text(f"Total: {s.get('total_bills', 0)}"),
                    ft.Text(f"Paid: {s.get('paid_bills', 0)}"),
                    ft.Text(f"Unpaid: {s.get('unpaid_bills', 0)}"),
                    ft.Text(f"Amount: ₹{s.get('total_amount', 0)}"),
                    ft.Text(f"Due: ₹{s.get('due_amount', 0)}"),
                ], spacing=20)
            )

            content_controls.append(ft.Divider())

            # 🔹 LIST
            if invoices:
                for inv in invoices:

                    mode_dd = ft.Dropdown(
                        width=150,
                        options=[
                            ft.dropdown.Option("Cash"),
                            ft.dropdown.Option("UPI"),
                            ft.dropdown.Option("Card"),
                            ft.dropdown.Option("Insurance"),
                        ],
                        value=inv.get("payment_mode") or "Cash"
                    )

                    content_controls.append(
                        ft.Container(
                            padding=12,
                            margin=ft.Margin.only(bottom=10),
                            bgcolor="#F0FDFA",
                            border_radius=10,
                            content=ft.Column([
                                ft.Text(f"{inv['invoice_number']} | {inv['bill_type']}", weight="bold"),
                                ft.Text(f"{inv['first_name']} {inv['last_name']}"),
                                ft.Text(f"Total: ₹{inv['total_amount']} | Paid: ₹{inv['paid_amount']} | Due: ₹{inv['due_amount']}"),
                                ft.Text(f"Payment: {inv['payment_status']}"),

                                ft.Row([
                                    mode_dd,
                                    ft.FilledButton(
                                        "Mark Paid",
                                        bgcolor="#0F766E",
                                        color="white",
                                        on_click=lambda e, iid=inv["invoice_id"], dd=mode_dd:
                                            mark_invoice_paid(iid, dd.value)
                                    )
                                ])
                            ])
                        )
                    )
            else:
                content_controls.append(ft.Text("No billing records found"))

        elif tab == "rec_overview":
            banner = ft.Container(
                bgcolor="#004D40", 
                padding=40, 
                border_radius=15, 
                margin= ft.Margin.only(bottom=20),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("Front Desk Operations", size=32, weight="bold", color=ft.Colors.WHITE), 
                                ft.Text("Manage patient flow, appointments, and billing efficiently.", size=16, color=ft.Colors.WHITE70)
                            ]
                        ), 
                        ft.Icon(ft.Icons.SUPPORT_AGENT, size=100, color=ft.Colors.WHITE24)
                    ]
                )
            )
            content_controls.append(banner)
            
            appt_card = ft.Card(
                ft.Container(
                    padding=25, 
                    width=320, 
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text("TODAY'S APPOINTMENTS", color=ft.Colors.GREY_600), 
                                    ft.Text("24 / 30", size=26, weight="bold")
                                ]
                            ), 
                            ft.ProgressRing(value=24/30, color=ft.Colors.TEAL, bgcolor=ft.Colors.GREY_200, width=50, height=50)
                        ]
                    )
                )
            )
            
            bill_card = ft.Card(
                ft.Container(
                    padding=25, 
                    width=320, 
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text("PENDING BILLS", color=ft.Colors.GREY_600), 
                                    ft.Text("5", size=26, weight="bold")
                                ]
                            ), 
                            ft.Icon(ft.Icons.WARNING_ROUNDED, color=ft.Colors.RED_400, size=40)
                        ]
                    )
                )
            )
            
            content_controls.append(
                ft.Row(
                    controls=[appt_card, bill_card]
                )
            )
        elif tab == "rec_billing":

            content_controls.append(
                ft.Text("Billing Desk", size=24, weight="bold")
            )

            preview_area = ft.Column(spacing=8)
            extra_items = []

            bill_type_dd = ft.Dropdown(
                label="Bill Type",
                width=200,
                options=[
                    ft.dropdown.Option("OPD"),
                    ft.dropdown.Option("LAB"),
                    ft.dropdown.Option("IPD"),
                ],
                value="OPD"
            )

            source_dd = ft.Dropdown(
                label="Select Source",
                width=300
            )
            extra_desc = ft.TextField(
                label="Extra Charge Description",
                width=250
            )

            extra_qty = ft.TextField(
                label="Qty",
                width=100,
                value="1"
            )

            extra_rate = ft.TextField(
                label="Unit Price",
                width=120
            )
            # =========================
            # REQUIRED CONTROLS
            # =========================

            bill_type_dd = ft.Dropdown(
                label="Bill Type",
                width=200,
                value="OPD",
                options=[
                    ft.dropdown.Option("OPD"),
                    ft.dropdown.Option("LAB"),
                    ft.dropdown.Option("IPD"),
                ]
            )

            source_dd = ft.Dropdown(
                label="Select Source",
                width=300
            )

            collect_now_sw = ft.Switch(
                label="Collect Payment Now",
                value=False,
                active_color="#0F766E"
            )

            payment_mode_dd = ft.Dropdown(
                label="Payment Mode",
                width=200,
                options=[
                    ft.dropdown.Option("Cash"),
                    ft.dropdown.Option("UPI"),
                    ft.dropdown.Option("Card"),
                    ft.dropdown.Option("Insurance"),
                ],
                value="Cash"
            )

            extra_desc = ft.TextField(label="Extra Description", width=250)
            extra_qty = ft.TextField(label="Qty", width=100, value="1")
            extra_rate = ft.TextField(label="Unit Price", width=120)

            preview_area = ft.Column(spacing=8)
            extra_items = []

            # =========================
            # LOAD SOURCES
            # =========================
            def load_sources(e):
                bill_type = bill_type_dd.value

                if bill_type == "OPD":
                    rows = get_query_data("""
                        SELECT c.consultation_id, p.first_name, p.last_name
                        FROM Consultation c
                        JOIN Patient p ON c.patient_id = p.patient_id
                        ORDER BY c.consultation_id DESC
                    """) or []

                    source_dd.options = [
                        ft.dropdown.Option(
                            key=str(r["consultation_id"]),
                            text=f"Consult #{r['consultation_id']} | {r['first_name']} {r['last_name']}"
                        )
                        for r in rows
                    ]

                elif bill_type == "LAB":
                    rows = get_query_data("""
                        SELECT lo.order_id, p.first_name, p.last_name
                        FROM LabOrder lo
                        JOIN Patient p ON lo.patient_id = p.patient_id
                        ORDER BY lo.order_id DESC
                    """) or []

                    source_dd.options = [
                        ft.dropdown.Option(
                            key=str(r["order_id"]),
                            text=f"Lab Order #{r['order_id']} | {r['first_name']} {r['last_name']}"
                        )
                        for r in rows
                    ]

                elif bill_type == "IPD":
                    rows = get_query_data("""
                        SELECT a.admission_id, p.first_name, p.last_name
                        FROM Admission a
                        JOIN Patient p ON a.patient_id = p.patient_id
                        ORDER BY a.admission_id DESC
                    """) or []

                    source_dd.options = [
                        ft.dropdown.Option(
                            key=str(r["admission_id"]),
                            text=f"Admission #{r['admission_id']} | {r['first_name']} {r['last_name']}"
                        )
                        for r in rows
                    ]

                source_dd.value = None
                page.update()

            # =========================
            # ADD EXTRA CHARGE
            # =========================
            def add_extra_charge(e):
                try:
                    extra_items.append({
                        "item_type": "Extra",
                        "description": extra_desc.value,
                        "quantity": int(extra_qty.value),
                        "unit_price": float(extra_rate.value)
                    })

                    preview_area.controls.append(
                        ft.Text(f"Added: {extra_desc.value} | Qty {extra_qty.value} | ₹{extra_rate.value}")
                    )
                    page.update()
                except:
                    show_snack("Invalid extra charge", ft.Colors.RED)

            # =========================
            # GENERATE BILL
            # =========================
            def generate_bill(e):

                if not source_dd.value:
                    show_snack("Select source first", ft.Colors.RED)
                    return

                bill_type = bill_type_dd.value
                items = []
                patient_id = None
                consultation_id = None
                lab_order_id = None
                admission_id = None

                # ---------- OPD ----------
                if bill_type == "OPD":
                    row = get_query_data("""
                        SELECT consultation_id, patient_id
                        FROM Consultation
                        WHERE consultation_id = %s
                    """, (source_dd.value,))

                    if not row:
                        show_snack("Consultation not found", ft.Colors.RED)
                        return

                    r = row[0]
                    patient_id = r["patient_id"]
                    consultation_id = r["consultation_id"]

                    items.append({
                        "item_type": "Consultation",
                        "description": "Doctor Consultation",
                        "quantity": 1,
                        "unit_price": 500
                    })

                # ---------- LAB ----------
                elif bill_type == "LAB":
                    row = get_query_data("""
                        SELECT patient_id FROM LabOrder WHERE order_id = %s
                    """, (source_dd.value,))

                    if not row:
                        show_snack("Lab order not found", ft.Colors.RED)
                        return

                    patient_id = row[0]["patient_id"]
                    lab_order_id = int(source_dd.value)

                    tests = get_query_data("""
                        SELECT t.test_name, t.price
                        FROM LabOrderItem li
                        JOIN LabTest t ON li.test_id = t.test_id
                        WHERE li.order_id = %s
                    """, (source_dd.value,))

                    for t in tests:
                        items.append({
                            "item_type": "Lab",
                            "description": t["test_name"],
                            "quantity": 1,
                            "unit_price": float(t["price"])
                        })

                # ---------- IPD ----------
                elif bill_type == "IPD":
                    row = get_query_data("""
                        SELECT
                            a.admission_id, a.patient_id,
                            a.admission_date, a.discharge_date,
                            r.room_number, r.daily_charge
                        FROM Admission a
                        JOIN Bed b ON a.bed_id = b.bed_id
                        JOIN Room r ON b.room_id = r.room_id
                        WHERE a.admission_id = %s
                    """, (source_dd.value,))

                    if not row:
                        show_snack("Admission not found", ft.Colors.RED)
                        return

                    r = row[0]
                    patient_id = r["patient_id"]
                    admission_id = r["admission_id"]

                    start = r["admission_date"]
                    end = r["discharge_date"] or datetime.datetime.now()
                    days = max(1, (end.date() - start.date()).days)

                    items.append({
                        "item_type": "Room",
                        "description": f"Room {r['room_number']} ({days} days)",
                        "quantity": days,
                        "unit_price": float(r["daily_charge"])
                    })

                # ---------- EXTRA ----------
                items.extend(extra_items)

                if not items:
                    show_snack("No bill items", ft.Colors.RED)
                    return

                # =========================
                # PREVIEW
                # =========================
                preview_area.controls.clear()
                total = 0

                for item in items:
                    item_total = item["quantity"] * item["unit_price"]
                    total += item_total

                    preview_area.controls.append(
                        ft.Text(
                            f"{item['description']} | Qty {item['quantity']} | ₹{item['unit_price']} | Total ₹{item_total}"
                        )
                    )

                preview_area.controls.append(
                    ft.Text(f"Grand Total: ₹{total}", weight="bold", size=16)
                )

                page.update()

                # =========================
                # SAVE INVOICE
                # =========================
                try:
                    invoice_id = save_invoice_record(
                        patient_id=patient_id,
                        bill_type=bill_type,
                        items=items,
                        collect_now=collect_now_sw.value,
                        payment_mode=payment_mode_dd.value,
                        notes=f"{bill_type} bill",
                        consultation_id=consultation_id,
                        lab_order_id=lab_order_id,
                        admission_id=admission_id
                    )

                    if invoice_id:
                        show_snack(f"Invoice Created ID: {invoice_id}", ft.Colors.GREEN)
                        nav_to("billing")

                except Exception as ex:
                    show_snack(f"Error: {ex}", ft.Colors.RED)

            # =========================
            # UI
            # =========================
            content_controls.append(
                ft.Container(
                    padding=16,
                    border_radius=12,
                    bgcolor=ft.Colors.WHITE,
                    content=ft.Column([
                        ft.Row([bill_type_dd, source_dd], spacing=12),
                        ft.Row([collect_now_sw, payment_mode_dd], spacing=12),
                        ft.Row([extra_desc, extra_qty, extra_rate], spacing=12),

                        ft.Row([
                            ft.FilledButton("Load Sources", bgcolor="#0F766E", color="white", on_click=load_sources),
                            ft.FilledButton("Add Extra Charge", bgcolor="#0F766E", color="white", on_click=add_extra_charge),
                            ft.FilledButton("Generate Bill", bgcolor="#0F766E", color="white", on_click=generate_bill),
                        ], spacing=12),

                        ft.Divider(),
                        ft.Text("Preview", weight="bold"),
                        preview_area
                    ], spacing=12)
                )
            )
        # =====================================================================
        # 5.4. MODULE: STAFF MANAGEMENT (THE BULLETPROOF UI FIX)
        # =====================================================================
        elif tab == "staff":
            level_data = get_query_data("SELECT access_level FROM Admin WHERE user_id = %s", (uid,))
            level = level_data[0]['access_level'] if level_data else "standard"

            # Common inputs
            us_in = ft.TextField(label="System Username", width=250)
            pa_in = ft.TextField(label="System Password", password=True, width=250)
            em_in = ft.TextField(label="System Email Address", width=250)
            fn_in = ft.TextField(label="First Name", width=250)
            ln_in = ft.TextField(label="Last Name", width=250)
            ph_in = ft.TextField(label="Phone Number", width=250)

            ro_drop = ft.Dropdown(
                label="Assign Role",
                width=250,
                options=[
                    ft.dropdown.Option("Doctor"),
                    ft.dropdown.Option("Receptionist"),
                    ft.dropdown.Option("Admin"),
                    ft.dropdown.Option("Lab Technician"),
                    ft.dropdown.Option("Pharmacist")
                ]
            )

            # Role-specific inputs
            acc_drop = ft.Dropdown(
                label="Admin Access Level",
                width=250,
                options=[ft.dropdown.Option("super"), ft.dropdown.Option("standard")]
            )
            gen_drop = ft.Dropdown(
                label="Gender",
                width=250,
                options=[
                    ft.dropdown.Option("Male"),
                    ft.dropdown.Option("Female"),
                    ft.dropdown.Option("Other")
                ]
            )
            dob_in = ft.TextField(label="DOB (YYYY-MM-DD)", width=250)
            spec_in = ft.TextField(label="Specialization", width=250)
            qual_in = ft.TextField(label="Qualifications", width=250)
            lic_in = ft.TextField(label="License Number", width=250)
            exp_in = ft.TextField(label="Years of Experience", width=250)
            dept_in = ft.TextField(label="Department ID", width=250)
            fee_in = ft.TextField(label="Consultation Fee (₹)", width=250)
            shift_drop = ft.Dropdown(
                label="Assigned Shift",
                width=250,
                options=[
                    ft.dropdown.Option("Morning"),
                    ft.dropdown.Option("Evening"),
                    ft.dropdown.Option("Night"),
                    ft.dropdown.Option("Rotating")
                ]
            )
            join_in = ft.TextField(label="Joining Date (YYYY-MM-DD)", width=250)
            bg_drop = ft.Dropdown(
                label="Blood Group",
                width=250,
                options=[
                    ft.dropdown.Option("A+"),
                    ft.dropdown.Option("O+"),
                    ft.dropdown.Option("B+"),
                    ft.dropdown.Option("AB+"),
                    ft.dropdown.Option("O-")
                ]
            )
            addr_in = ft.TextField(label="Full Residential Address", width=520)
            counter_in = ft.TextField(label="Desk/Counter Number", width=250)

            dynamic_fields = ft.Column(controls=[])

            def update_fields(e):
                role_value = ro_drop.value
                dynamic_fields.controls.clear()

                if role_value == "Doctor":
                    dynamic_fields.controls.extend([
                        ft.Row(controls=[gen_drop, dob_in]),
                        ft.Row(controls=[spec_in, qual_in]),
                        ft.Row(controls=[lic_in, exp_in]),
                        ft.Row(controls=[dept_in, fee_in]),
                        ft.Row(controls=[shift_drop, join_in]),
                        ft.Row(controls=[bg_drop]),
                        addr_in
                    ])

                elif role_value == "Receptionist":
                    dynamic_fields.controls.extend([
                        ft.Row(controls=[gen_drop, shift_drop]),
                        ft.Row(controls=[counter_in, join_in])
                    ])

                elif role_value == "Lab Technician":
                    dynamic_fields.controls.extend([
                        ft.Row(controls=[gen_drop, shift_drop]),
                        ft.Row(controls=[spec_in, qual_in]),
                        ft.Row(controls=[join_in])
                    ])

                elif role_value == "Pharmacist":
                    dynamic_fields.controls.extend([
                        ft.Row(controls=[lic_in, shift_drop])
                    ])

                elif role_value == "Admin":
                    dynamic_fields.controls.append(ft.Row(controls=[acc_drop]))

                page.update()

            ro_drop.on_change = update_fields
            

            def execute_hire(e):
                data_dict = {
                    "role": ro_drop.value,
                    "user": us_in.value,
                    "pass": pa_in.value,
                    "email": em_in.value,
                    "fname": fn_in.value,
                    "lname": ln_in.value,
                    "phone": ph_in.value,
                    "access": acc_drop.value,
                    "gender": gen_drop.value,
                    "dob": dob_in.value,
                    "spec": spec_in.value,
                    "qual": qual_in.value,
                    "lic": lic_in.value,
                    "exp": exp_in.value,
                    "dept": dept_in.value,
                    "fee": fee_in.value,
                    "shift": shift_drop.value,
                    "join": join_in.value,
                    "bg": bg_drop.value,
                    "addr": addr_in.value,
                    "counter": counter_in.value
                }

                if hire_staff_db(data_dict):
                    hire_dlg.open = False
                    page.update()
                    show_snack("Personnel Successfully Registered in Database!", ft.Colors.GREEN)
                    nav_to("staff")
                else:
                    show_snack("Registration Failed. Check unique constraints (e.g. Username/Email).", ft.Colors.RED)

            hire_dlg = ft.AlertDialog(
                title=ft.Text("Register New Personnel", weight="bold"),
                content=ft.Container(
                    width=570,
                    content=ft.Column(
                        controls=[
                            ft.Text("System Access Credentials", weight="bold", color=ft.Colors.BLUE_900),
                            ft.Row(controls=[us_in, pa_in]),
                            ft.Row(controls=[em_in, ro_drop]),
                            ft.Divider(),
                            ft.Text("Basic Identity", weight="bold", color=ft.Colors.BLUE_900),
                            ft.Row(controls=[fn_in, ln_in]),
                            ft.Row(controls=[ph_in]),
                            ft.Divider(),
                            dynamic_fields
                        ],
                        tight=True,
                        scroll=ft.ScrollMode.AUTO
                    )
                ),
                actions=[
                    ft.FilledButton(
                        "Save Complete Profile to Database",
                        on_click=execute_hire,
                        style=admin_btn_style
                    )
                ]
            )

            def open_staff_profile(staff_member):
                table_map = {
                    "Admin": "Admin",
                    "Doctor": "Doctor",
                    "Receptionist": "Receptionist",
                    "Lab Technician": "LabTechnician",
                    "Pharmacist": "Pharmacist"
                }
                table_name = table_map.get(staff_member['role_name'], staff_member['role_name'].replace(" ", ""))

                profile_query = f"SELECT * FROM {table_name} WHERE user_id = %s"
                profile_data = get_query_data(profile_query, (staff_member['user_id'],))
                p = profile_data[0] if profile_data else {}

                extra_controls = []
                if staff_member['role_name'] == "Doctor":
                    extra_controls.extend([
                        ft.Text(f"Specialization: {p.get('specialization')} | Qualification: {p.get('qualification')}"),
                        ft.Text(f"Medical License: {p.get('license_number')} | Experience: {p.get('experience_years')} yrs"),
                        ft.Text(f"Consultation Fee: ₹{p.get('consultation_fee')} | Active Shift: {p.get('shift')}"),
                        ft.Text(f"Joining Date: {p.get('joining_date')} | Dept ID: {p.get('dept_id')}")
                    ])
                elif staff_member['role_name'] == "Admin":
                    extra_controls.append(ft.Text(f"Employee ID: {p.get('employee_id')} | Access Rights: {str(p.get('access_level')).upper()}"))
                elif staff_member['role_name'] == "Receptionist":
                    extra_controls.extend([
                        ft.Text(f"Employee ID: {p.get('employee_id')} | Active Shift: {p.get('shift')}"),
                        ft.Text(f"Counter Number: {p.get('counter_number')} | Joining Date: {p.get('joining_date')}")
                    ])
                elif staff_member['role_name'] == "Lab Technician":
                    extra_controls.extend([
                        ft.Text(f"Employee ID: {p.get('employee_id')} | Active Shift: {p.get('shift')}"),
                        ft.Text(f"Specialization: {p.get('specialization')} | Qualification: {p.get('qualification')}"),
                        ft.Text(f"Joining Date: {p.get('joining_date')}")
                    ])
                elif staff_member['role_name'] == "Pharmacist":
                    extra_controls.append(ft.Text(f"Pharmacy License: {p.get('license_number')} | Active Shift: {p.get('shift')}"))

                staff_dlg = ft.AlertDialog(
                    title=ft.Text(f"Personnel Profile: {staff_member['username']}", weight="bold", color=ft.Colors.BLUE_900),
                    content=ft.Container(
                        width=500,
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text(f"System ID: {staff_member['user_id']}", weight="bold"),
                                        ft.Text(f"Role: {staff_member['role_name']}", weight="bold", color=ft.Colors.GREY_600)
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                ),
                                ft.Divider(),
                                ft.Text("Basic Info", weight="bold", color=ft.Colors.GREY_600),
                                ft.Text(f"Name: {p.get('first_name', 'Data Missing')} {p.get('last_name', '')}"),
                                ft.Text(f"Email: {staff_member['email']} | Phone: {p.get('phone', 'N/A')}"),
                                ft.Text(
                                    f"System Access: {'GRANTED' if staff_member['is_active'] else 'REVOKED'}",
                                    color=ft.Colors.GREEN if staff_member['is_active'] else ft.Colors.RED,
                                    weight="bold"
                                ),
                                ft.Divider(),
                                ft.Text("Schema & Operational Attributes", weight="bold", color=ft.Colors.GREY_600),
                                *extra_controls
                            ],
                            tight=True,
                            scroll=ft.ScrollMode.AUTO
                        )
                    ),
                    actions=[
                        ft.TextButton(
                            "Close Profile",
                            on_click=lambda e: setattr(staff_dlg, 'open', False) or page.update()
                        )
                    ]
                )
                page.overlay.append(staff_dlg)
                staff_dlg.open = True
                page.update()

            staff_data = get_query_data(
                "SELECT u.user_id, u.username, r.role_name, u.email, u.is_active FROM Users u JOIN Role r ON u.role_id = r.role_id"
            )

            if not staff_data:
                content_controls.append(ft.Text("No personnel data found in system.", color=ft.Colors.GREY))
            else:
                table_rows = []
                for s in staff_data:
                    view_btn = ft.IconButton(
                        icon=ft.Icons.VISIBILITY,
                        icon_color="#0F766E",
                        on_click=lambda e, data=s: open_staff_profile(data)
                    )
                    table_rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(s['username'])),
                                ft.DataCell(ft.Text(s['role_name'])),
                                ft.DataCell(ft.Text(s['email'])),
                                ft.DataCell(view_btn)
                            ]
                        )
                    )

                if level == "super":
                    content_controls.append(
                        ft.FilledButton(
                            "Register New Staff Member",
                            icon=ft.Icons.PERSON_ADD,
                            style=admin_btn_style,
                            on_click=lambda e: page.overlay.append(hire_dlg) or setattr(hire_dlg, 'open', True) or page.update()
                        )
                    )

                content_controls.extend([
                    ft.Divider(),
                    ft.Text("Click the eye icon to view comprehensive schema attributes for any staff member.", color=ft.Colors.GREY),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Username")),
                            ft.DataColumn(ft.Text("Role")),
                            ft.DataColumn(ft.Text("Email Address")),
                            ft.DataColumn(ft.Text("Action"))
                        ],
                        rows=table_rows
                    )
                ])

        # =====================================================================
        # 5.5. MODULE: STAFF SCHEDULES (RESTORED AS REQUESTED)
        # =====================================================================
        elif tab == "schedules":
            schedule_query = """
                SELECT s.schedule_id, u.username, r.role_name, s.work_date, s.shift_start, s.shift_end, s.status 
                FROM StaffSchedule s 
                JOIN Users u ON s.user_id = u.user_id 
                JOIN Role r ON s.role_id = r.role_id 
                ORDER BY s.work_date DESC, s.shift_start ASC
            """
            sched_data = get_query_data(schedule_query)

            if not sched_data:
                content_controls.append(
                    ft.Text("No staff schedules currently exist in the database.", color=ft.Colors.GREY)
                )
            else:
                s_rows = []
                for s in sched_data:
                    if s['status'] == 'Present':
                        status_color = ft.Colors.GREEN
                    elif s['status'] == 'Scheduled':
                        status_color = ft.Colors.ORANGE
                    else:
                        status_color = ft.Colors.RED
                        
                    s_rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(s['schedule_id']))),
                                ft.DataCell(ft.Text(s['username'])),
                                ft.DataCell(ft.Text(s['role_name'])),
                                ft.DataCell(ft.Text(str(s['work_date']))),
                                ft.DataCell(ft.Text(f"{s['shift_start']} - {s['shift_end']}")),
                                ft.DataCell(
                                    ft.Container(
                                        content=ft.Text(s['status'].upper(), weight="bold", color=ft.Colors.WHITE, size=11), 
                                        bgcolor=status_color, 
                                        padding=5, 
                                        border_radius=5
                                    )
                                )
                            ]
                        )
                    )
                
                content_controls.extend([
                    ft.Text("Enterprise Staff Schedule Logs", weight="bold", size=20), 
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Schedule ID")), 
                            ft.DataColumn(ft.Text("Staff Username")), 
                            ft.DataColumn(ft.Text("Role")), 
                            ft.DataColumn(ft.Text("Work Date")), 
                            ft.DataColumn(ft.Text("Shift Time")),
                            ft.DataColumn(ft.Text("Attendance Status"))
                        ], 
                        rows=s_rows
                    )
                ])

        # =====================================================================
        # 5.6. MODULE: COMPREHENSIVE PATIENT REGISTRATION
        # =====================================================================
        elif tab == "reg_patient":
            fn = ft.TextField(label="First Name", width=250)
            ln = ft.TextField(label="Last Name", width=250)
            dob = ft.TextField(label="Date of Birth (YYYY-MM-DD)", width=250)
            gen = ft.Dropdown(label="Gender", width=250, options=[
                ft.dropdown.Option("Male"),
                ft.dropdown.Option("Female"),
                ft.dropdown.Option("Other")
            ])
            bg = ft.Dropdown(label="Blood Group", width=250, options=[
                ft.dropdown.Option("A+"),
                ft.dropdown.Option("O+"),
                ft.dropdown.Option("B+"),
                ft.dropdown.Option("AB+"),
                ft.dropdown.Option("O-"),
                ft.dropdown.Option("A-"),
                ft.dropdown.Option("B-")
            ])
            ph = ft.TextField(label="Phone Number", width=250)
            em = ft.TextField(label="Email Address", width=250)
            addr = ft.TextField(label="Residential Address", width=520)
            city = ft.TextField(label="City", width=160)
            st = ft.TextField(label="State", width=160)
            pin = ft.TextField(label="Postal Code", width=160)
            e_name = ft.TextField(label="Emergency Contact Name", width=250)
            e_phone = ft.TextField(label="Emergency Phone", width=250)
            e_rel = ft.TextField(label="Relationship", width=250)
            i_prov = ft.TextField(label="Insurance Provider", width=250)
            i_pol = ft.TextField(label="Policy Number", width=250)

            def save_comprehensive_patient(e):
                conn = get_db_connection()
                if not conn:
                    return

                cursor = conn.cursor(dictionary=True)
                try:
                    rec_id = page.session.store.get("rec_id")
                    if not rec_id:
                        show_snack("Receptionist session missing. Please log in again.", ft.Colors.RED)
                        return

                    cursor.execute("SELECT MAX(patient_id) as max_id FROM Patient")
                    res = cursor.fetchone()
                    next_id = (res['max_id'] or 0) + 1 if res else 1
                    auto_reg_no = f"AHL-PT-{next_id:04d}"

                    query = """
                        INSERT INTO Patient (
                            registration_no, first_name, last_name, gender, date_of_birth, blood_group, 
                            phone, email, address, city, state, pincode, 
                            emergency_contact_name, emergency_contact_phone, emergency_contact_rel, 
                            insurance_provider, insurance_policy_no, registered_by
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    params = (
                        auto_reg_no, fn.value, ln.value, gen.value, dob.value, bg.value,
                        ph.value, em.value, addr.value, city.value, st.value, pin.value,
                        e_name.value, e_phone.value, e_rel.value, i_prov.value, i_pol.value, rec_id
                    )

                    cursor.execute(query, params)
                    conn.commit()
                    show_snack(f"Success! Auto-Generated Patient ID: {auto_reg_no}", ft.Colors.GREEN)
                    nav_to("reg_patient")
                except Exception as ex:
                    conn.rollback()
                    show_snack(f"Database Error: {ex}", ft.Colors.RED)
                finally:
                    cursor.close()
                    conn.close()

            content_controls.append(
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        spacing=15,
                        scroll=ft.ScrollMode.AUTO,
                        controls=[
                            ft.Text("General Medical Information", weight="bold", color=ft.Colors.TEAL_900),
                            ft.Text(
                                "Note: Registration Number (AHL-PT-XXXX) is generated automatically upon save.",
                                italic=True,
                                color=ft.Colors.GREY
                            ),
                            ft.ResponsiveRow(
                                controls=[
                                    ft.Container(fn, col=4),
                                    ft.Container(ln, col=4),
                                    ft.Container(dob, col=4),
                                ]
                            ),
                            ft.ResponsiveRow(
                                controls=[
                                    ft.Container(gen, col=3),
                                    ft.Container(bg, col=3),
                                    ft.Container(ph, col=3),
                                    ft.Container(em, col=3),
                                ]
                            ),
                            ft.Divider(),
                            ft.Text("Location & Demographics", weight="bold", color=ft.Colors.TEAL_900),
                            ft.ResponsiveRow(
                                controls=[
                                    ft.Container(addr, col=6),
                                    ft.Container(city, col=2),
                                    ft.Container(st, col=2),
                                    ft.Container(pin, col=2),
                                ]
                            ),
                            ft.Divider(),
                            ft.Text("Emergency Contacts & Insurance", weight="bold", color=ft.Colors.TEAL_900),
                            ft.ResponsiveRow(
                                controls=[
                                    ft.Container(e_name, col=4),
                                    ft.Container(e_phone, col=4),
                                    ft.Container(e_rel, col=4),
                                ]
                            ),
                            ft.ResponsiveRow(
                                controls=[
                                    ft.Container(i_prov, col=6),
                                    ft.Container(i_pol, col=6),
                                ]
                            ),
                            ft.FilledButton(
                                "Commit Patient to Database",
                                icon=ft.Icons.SAVE,
                                style=rec_btn_style,
                                on_click=save_comprehensive_patient
                            )
                        ]
                    )
                )
            )

    # =====================================================================
    # 5.7. MODULE: PATIENT SEARCH
    # =====================================================================
        elif tab == "search_patient":
            def search_patient(e):
                conn = get_db_connection()
                if not conn:
                    return

            def save_comprehensive_patient(e):
                conn = get_db_connection()
                if not conn:
                    return

                cursor = conn.cursor(dictionary=True)
                try:
                    rec_id = page.session.store.get("rec_id")
                    if not rec_id:
                        show_snack("Receptionist session missing. Please log in again.", ft.Colors.RED)
                        return

                    cursor.execute("SELECT MAX(patient_id) as max_id FROM Patient")
                    res = cursor.fetchone()
                    next_id = (res['max_id'] or 0) + 1 if res else 1
                    auto_reg_no = f"AHL-PT-{next_id:04d}"

                    query = """
                        INSERT INTO Patient (
                            registration_no, first_name, last_name, gender, date_of_birth, blood_group, 
                            phone, email, address, city, state, pincode, 
                            emergency_contact_name, emergency_contact_phone, emergency_contact_rel, 
                            insurance_provider, insurance_policy_no, registered_by
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    params = (
                        auto_reg_no, fn.value, ln.value, gen.value, dob.value, bg.value,
                        ph.value, em.value, addr.value, city.value, st.value, pin.value,
                        e_name.value, e_phone.value, e_rel.value, i_prov.value, i_pol.value, rec_id
                    )

                    cursor.execute(query, params)
                    conn.commit()
                    show_snack(f"Success! Auto-Generated Patient ID: {auto_reg_no}", ft.Colors.GREEN)
                    nav_to("reg_patient")
                except Exception as ex:
                    conn.rollback()
                    show_snack(f"Database Error: {ex}", ft.Colors.RED)
                finally:
                    cursor.close()
                    conn.close()

        # =====================================================================
        # 5.7. MODULE: PATIENT MASTER DIRECTORY
        # =====================================================================
        elif tab == "patient_billing":
            pid = page.session.store.get("patient_id")
            bills = get_query_data("""
                SELECT
                    invoice_number, bill_type, invoice_date,
                    subtotal, total_amount, paid_amount, due_amount,
                    payment_status, payment_mode, notes
                FROM Invoice
                WHERE patient_id = %s
                ORDER BY invoice_date DESC
            """, (pid,))

            content_controls.append(ft.Text("Bills & Payments", size=20, weight="bold"))

            if bills:
                for b in bills:
                    content_controls.append(
                        ft.Container(
                            margin=ft.Margin.only(bottom=12),
                            padding=14,
                            border_radius=12,
                            bgcolor="#F0FDFA",
                            content=ft.Column([
                                ft.Text(f"{b['invoice_number']} | {b.get('bill_type') or 'N/A'}", weight="bold"),
                                ft.Text(f"Date: {fmt_dt(b.get('invoice_date'))}"),
                                ft.Text(f"Subtotal: ₹{b.get('subtotal') or 0} | Total: ₹{b.get('total_amount') or 0}"),
                                ft.Text(f"Paid: ₹{b.get('paid_amount') or 0} | Due: ₹{b.get('due_amount') or 0}"),
                                ft.Text(f"Status: {b.get('payment_status') or 'N/A'} | Mode: {b.get('payment_mode') or 'N/A'}"),
                                ft.Text(f"Notes: {b.get('notes') or 'N/A'}"),
                            ])
                        )
                    )
            else:
                content_controls.append(ft.Text("No bills found"))

        elif tab == "patient_lab_results":
            pid = page.session.store.get("patient_id")
            results = get_query_data("""
                SELECT
                    lr.result_value,
                    lr.unit,
                    lr.normal_range,
                    lr.status,
                    lr.remarks,
                    lr.reported_at,
                    t.test_name
                FROM LabResult lr
                JOIN LabOrderItem loi ON lr.order_item_id = loi.order_item_id
                JOIN LabOrder lo ON loi.order_id = lo.order_id
                JOIN LabTest t ON loi.test_id = t.test_id
                WHERE lo.patient_id = %s
                ORDER BY lr.reported_at DESC
            """, (pid,))

            content_controls.append(ft.Text("Lab Results", size=20, weight="bold"))

            if results:
                for r in results:
                    content_controls.append(
                        ft.Container(
                            margin=ft.Margin.only(bottom=12),
                            padding=14,
                            border_radius=12,
                            bgcolor="#F0FDFA",
                            content=ft.Column([
                                ft.Text(r.get("test_name") or "N/A", weight="bold"),
                                ft.Text(f"Result: {r.get('result_value') or 'N/A'} {r.get('unit') or ''}"),
                                ft.Text(f"Normal Range: {r.get('normal_range') or 'N/A'}"),
                                ft.Text(f"Status: {r.get('status') or 'N/A'}"),
                                ft.Text(f"Reported: {fmt_dt(r.get('reported_at'))}"),
                                ft.Text(f"Remarks: {r.get('remarks') or 'N/A'}"),
                            ])
                        )
                    )
            else:
                content_controls.append(ft.Text("No lab results available"))

        elif tab == "patient_allergies":
            pid = page.session.store.get("patient_id")
            allergies = get_query_data("""
                SELECT allergen, reaction, severity
                FROM Allergy
                WHERE patient_id = %s
                ORDER BY severity
            """, (pid,))

            content_controls.append(ft.Text("Allergies", size=20, weight="bold"))

            if allergies:
                for a in allergies:
                    content_controls.append(
                        ft.Container(
                            margin=ft.Margin.only(bottom=12),
                            padding=14,
                            border_radius=12,
                            bgcolor="#F0FDFA",
                            content=ft.Column([
                                ft.Text(a.get("allergen") or "N/A", weight="bold"),
                                ft.Text(f"Reaction: {a.get('reaction') or 'N/A'}"),
                                ft.Text(f"Severity: {a.get('severity') or 'N/A'}"),
                            ])
                        )
                    )
            else:
                content_controls.append(ft.Text("No allergies recorded"))

        elif tab == "patient_history":
            pid = page.session.store.get("patient_id")
            history = get_query_data("""
                SELECT condition_name, diagnosed_date, status, notes
                FROM MedicalHistory
                WHERE patient_id = %s
                ORDER BY diagnosed_date DESC
            """, (pid,))

            content_controls.append(ft.Text("Medical History", size=20, weight="bold"))

            if history:
                for h in history:
                    content_controls.append(
                        ft.Container(
                            margin=ft.Margin.only(bottom=12),
                            padding=14,
                            border_radius=12,
                            bgcolor="#F0FDFA",
                            content=ft.Column([
                                ft.Text(h.get("condition_name") or "N/A", weight="bold"),
                                ft.Text(f"Diagnosed: {h.get('diagnosed_date') or 'N/A'}"),
                                ft.Text(f"Status: {h.get('status') or 'N/A'}"),
                                ft.Text(f"Notes: {h.get('notes') or 'N/A'}"),
                            ])
                        )
                    )
            else:
                content_controls.append(ft.Text("No medical history available")) 
        elif tab == "patient_appointments":
            pid = page.session.store.get("patient_id")
            appts = get_query_data("""
                SELECT
                    a.appointment_id,
                    a.appointment_date,
                    a.appointment_time,
                    a.token_number,
                    a.reason,
                    a.type,
                    a.status,
                    d.first_name AS doctor_first,
                    d.last_name AS doctor_last
                FROM Appointment a
                JOIN Doctor d ON a.doctor_id = d.doctor_id
                WHERE a.patient_id = %s
                ORDER BY a.appointment_date DESC, a.appointment_time DESC
            """, (pid,))

            content_controls.append(ft.Text("Appointments", size=20, weight="bold"))

            if appts:
                for a in appts:
                    content_controls.append(
                        ft.Container(
                            margin=ft.Margin.only(bottom=12),
                            padding=14,
                            border_radius=12,
                            bgcolor="#F0FDFA",
                            content=ft.Column([
                                ft.Text(f"Appointment #{a['appointment_id']}", weight="bold"),
                                ft.Text(f"Dr. {a['doctor_first']} {a['doctor_last']}"),
                                ft.Text(f"Date: {a['appointment_date']} | Time: {a['appointment_time']} | Token: {a.get('token_number') or 'N/A'}"),
                                ft.Text(f"Type: {a.get('type') or 'N/A'} | Status: {a.get('status') or 'N/A'}"),
                                ft.Text(f"Reason: {a.get('reason') or 'N/A'}"),
                            ])
                        )
                    )
            else:
                content_controls.append(ft.Text("No appointments found"))
        elif tab == "patient_profile":
            pid = page.session.store.get("patient_id")
            patient = get_query_data("""
                SELECT p.*, u.username, u.email AS login_email
                FROM Patient p
                LEFT JOIN Users u ON p.user_id = u.user_id
                WHERE p.patient_id = %s
            """, (pid,))

            if not patient:
                content_controls.append(ft.Text("Patient not found"))
                return

            p = patient[0]

            content_controls.append(ft.Text("My Profile", size=20, weight="bold"))
            content_controls.append(
                ft.Container(
                    padding=14,
                    border_radius=12,
                    bgcolor="#F0FDFA",
                    content=ft.Column([
                        ft.Text(f"Name: {p['first_name']} {p['last_name']}", weight="bold"),
                        ft.Text(f"Username: {p.get('username') or 'N/A'}"),
                        ft.Text(
                            f"Registered By: {p.get('reg_first_name') or 'N/A'} {p.get('reg_last_name') or ''} "
                            f"(ID: {p.get('reg_id') or 'N/A'})"
                        ),
                        ft.Text(f"Email: {p.get('login_email') or p.get('email') or 'N/A'}"),
                        ft.Text(f"Gender: {p.get('gender') or 'N/A'}"),
                        ft.Text(f"DOB: {p.get('date_of_birth') or 'N/A'}"),
                        ft.Text(f"Blood Group: {p.get('blood_group') or 'N/A'}"),
                        ft.Text(f"Phone: {p.get('phone') or 'N/A'}"),
                        ft.Text(f"Address: {p.get('address') or 'N/A'}"),
                        ft.Text(f"City: {p.get('city') or 'N/A'} | State: {p.get('state') or 'N/A'} | Pincode: {p.get('pincode') or 'N/A'}"),
                        ft.Text(f"Emergency Contact: {p.get('emergency_contact_name') or 'N/A'} | {p.get('emergency_contact_phone') or 'N/A'}"),
                        ft.Text(f"Insurance: {p.get('insurance_provider') or 'N/A'} | Policy: {p.get('insurance_policy_no') or 'N/A'}"),
                    ], spacing=8)
                )
            )
    
        elif tab == "patient_dashboard":
            pid = page.session.store.get("patient_id")
            if not pid:
                content_controls.append(ft.Text("No patient session found. Please log in again."))
                return

            p = get_query_data("""
                SELECT 
                    p.*,
                    u.username,
                    r.receptionist_id AS reg_id,
                    r.first_name AS reg_first_name,
                    r.last_name AS reg_last_name
                FROM Patient p
                LEFT JOIN Users u ON p.user_id = u.user_id
                LEFT JOIN Receptionist r ON p.registered_by = r.receptionist_id
                WHERE p.patient_id = %s
            """, (pid,))

            if not p:
                content_controls.append(ft.Text("Patient record not found"))
                return

            p = p[0]

            appt_count = get_query_data("SELECT COUNT(*) AS c FROM Appointment WHERE patient_id=%s", (pid,))
            hist_count = get_query_data("SELECT COUNT(*) AS c FROM MedicalHistory WHERE patient_id=%s", (pid,))
            allergy_count = get_query_data("SELECT COUNT(*) AS c FROM Allergy WHERE patient_id=%s", (pid,))
            bill_count = get_query_data("SELECT COUNT(*) AS c FROM Invoice WHERE patient_id=%s", (pid,))

            content_controls.append(
                ft.Container(
                    padding=16,
                    border_radius=12,
                    bgcolor="#F0FDFA",
                    content=ft.Column([
                        ft.Text(f"Welcome, {p['first_name']} {p['last_name']}", size=24, weight="bold"),
                        ft.Text(f"Patient ID: {p['patient_id']} | Reg No: {p['registration_no']}"),
                        ft.Text(f"Username: {p.get('username') or 'N/A'}"),
                        ft.Text(
                            f"Registered By: {p.get('reg_first_name') or 'N/A'} {p.get('reg_last_name') or ''} "
                            f"(ID: {p.get('reg_id') or 'N/A'})"
                        ),
                        ft.Text(f"Blood Group: {p.get('blood_group') or 'N/A'} | Phone: {p.get('phone') or 'N/A'}"),
                        ft.Row([
                            ft.Container(padding=12, bgcolor=ft.Colors.WHITE, border_radius=10,
                                        content=ft.Text(f"Appointments: {appt_count[0]['c'] if appt_count else 0}")),
                            ft.Container(padding=12, bgcolor=ft.Colors.WHITE, border_radius=10,
                                        content=ft.Text(f"Medical History: {hist_count[0]['c'] if hist_count else 0}")),
                            ft.Container(padding=12, bgcolor=ft.Colors.WHITE, border_radius=10,
                                        content=ft.Text(f"Allergies: {allergy_count[0]['c'] if allergy_count else 0}")),
                            ft.Container(padding=12, bgcolor=ft.Colors.WHITE, border_radius=10,
                                        content=ft.Text(f"Bills: {bill_count[0]['c'] if bill_count else 0}")),
                        ], spacing=12)
                    ])
                )
            )

            content_controls.append(
                ft.Row([
                    ft.FilledButton("My Profile", bgcolor="#0F766E", color=ft.Colors.WHITE, on_click=lambda e: nav_to("patient_profile")),
                    ft.FilledButton("Appointments", bgcolor="#0F766E", color=ft.Colors.WHITE, on_click=lambda e: nav_to("patient_appointments")),
                    ft.FilledButton("Medical History", bgcolor="#0F766E", color=ft.Colors.WHITE, on_click=lambda e: nav_to("patient_history")),
                    ft.FilledButton("Allergies", bgcolor="#0F766E", color=ft.Colors.WHITE, on_click=lambda e: nav_to("patient_allergies")),
                    ft.FilledButton("Lab Results", bgcolor="#0F766E", color=ft.Colors.WHITE, on_click=lambda e: nav_to("patient_lab_results")),
                    ft.FilledButton("Bills", bgcolor="#0F766E", color=ft.Colors.WHITE, on_click=lambda e: nav_to("patient_billing")),
                ], spacing=10)
            )
        elif tab == "patients":
            def open_patient_profile(p):
                patient_dlg = ft.AlertDialog(
                    title=ft.Text(f"Comprehensive Profile: {p['first_name']} {p['last_name']}", weight="bold", color="#0F766E"),
                    content=ft.Container(
                        width=650, 
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text(f"Reg No: {p['registration_no']}", weight="bold"), 
                                        ft.Text(f"Database ID: {p['patient_id']}")
                                    ], 
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                ), 
                                ft.Divider(),
                                ft.Text("Personal Information", weight="bold", color=ft.Colors.GREY_600), 
                                ft.Text(f"Date of Birth: {p['date_of_birth']} | Gender: {p['gender']} | Blood Group: {p['blood_group']}"), 
                                ft.Text(f"Phone: {p['phone']} | Email: {p['email']}"), 
                                ft.Divider(),
                                ft.Text("Residential Address", weight="bold", color=ft.Colors.GREY_600), 
                                ft.Text(f"{p['address']}, {p['city']}, {p['state']} - {p['pincode']}"), 
                                ft.Divider(),
                                ft.Text("Emergency Details & Health Insurance", weight="bold", color=ft.Colors.GREY_600), 
                                ft.Text(f"Contact Name: {p['emergency_contact_name']} ({p['emergency_contact_rel']}) - {p['emergency_contact_phone']}"), 
                                ft.Text(f"Provider: {p['insurance_provider']} | Policy No: {p['insurance_policy_no']}"),
                                ft.Text(f"Account Created: {p['registered_at']}", size=10, color=ft.Colors.GREY_400)
                            ], 
                            tight=True, 
                            scroll=ft.ScrollMode.AUTO
                        )
                    ),
                    actions=[
                        ft.OutlinedButton(
                            "Close Window",
                            style=ft.ButtonStyle(
                                color="#0F766E" 
                            ),
                            on_click=lambda e: setattr(patient_dlg, 'open', False) or page.update()
                        )
                    ]
                )
                page.overlay.append(patient_dlg)
                patient_dlg.open = True
                page.update()

            patient_data = get_query_data("SELECT * FROM Patient")
            if not patient_data: 
                content_controls.append(ft.Text("No patients currently exist in the database.", color=ft.Colors.GREY))
            else:
                p_rows = []
                for p in patient_data:
                    eye_btn = ft.IconButton(
                        icon=ft.Icons.VISIBILITY, 
                        icon_color="#0F766E", 
                        on_click=lambda e, data=p: open_patient_profile(data)
                    )
                    p_rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(f"{p['registration_no'] or 'N/A'}")), 
                                ft.DataCell(ft.Text(f"{p['first_name']} {p['last_name']}")), 
                                ft.DataCell(ft.Text(p['phone'] or 'N/A')), 
                                ft.DataCell(eye_btn)
                            ]
                        )
                    )
                
                content_controls.extend([
                    ft.Text("Patient Master Directory. Click the eye icon to retrieve full schema details.", color=ft.Colors.GREY), 
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Registration No.")), 
                            ft.DataColumn(ft.Text("Full Name")), 
                            ft.DataColumn(ft.Text("Contact Number")), 
                            ft.DataColumn(ft.Text("Actions"))
                        ], 
                        rows=p_rows
                    )
                ])
        
        # =====================================================================
        # 5.8. MODULE: APPOINTMENTS & SCHEDULING
        # =====================================================================
        elif tab == "book_appt":
            rec_id = page.session.store.get("rec_id")
            
            patient_list = get_query_data("SELECT patient_id, first_name, last_name, registration_no FROM Patient")
            doctor_list = get_query_data("SELECT doctor_id, first_name, last_name, specialization FROM Doctor")
            
            p_dropdown = ft.Dropdown(
                label="Select Registered Patient", 
                width=300, 
                options=[ft.dropdown.Option(key=str(p['patient_id']), text=f"{p['registration_no']} - {p['first_name']} {p['last_name']}") for p in patient_list]
            )
            d_dropdown = ft.Dropdown(
                label="Assign Specialist Doctor", 
                width=300, 
                options=[ft.dropdown.Option(key=str(d['doctor_id']), text=f"Dr. {d['first_name']} ({d['specialization']})") for d in doctor_list]
            )
            
            appt_date = ft.TextField(label="Date (YYYY-MM-DD)", width=200)
            appt_time = ft.TextField(label="Time (HH:MM)", width=200)
            appt_type = ft.Dropdown(
                label="Consultation Type",
                width=200,
                options=[
                    ft.dropdown.Option("OPD"),
                    ft.dropdown.Option("IPD"),
                    ft.dropdown.Option("Follow-up"),
                    ft.dropdown.Option("Emergency"),
                    ft.dropdown.Option("Online")
                ]
            )            
            token_num = ft.TextField(label="Token / Queue Number", width=200)
            visit_reason = ft.TextField(label="Primary Reason for Visit", width=450)
            internal_notes = ft.TextField(label="Internal Desk Notes", width=450)

            def execute_booking(e):
                try:
                    date_obj = datetime.datetime.strptime(appt_date.value, "%Y-%m-%d")
                    day_of_week_str = date_obj.strftime("%a")

                    token_value = token_num.value.strip()
                    if not token_value.isdigit():
                        show_snack("Token Number must be a whole number.", ft.Colors.RED)
                        return
                    token_value = int(token_value)

                    avail_check = get_query_data(
                        "SELECT * FROM DoctorAvailability WHERE doctor_id=%s AND day_of_week=%s",
                        (d_dropdown.value, day_of_week_str)
                    )
                    if not avail_check:
                        show_snack(f"Validation Failed: Doctor is NOT scheduled to work on {day_of_week_str}.", ft.Colors.RED)
                        return

                    query = """
                        INSERT INTO Appointment
                        (patient_id, doctor_id, receptionist_id, appointment_date, appointment_time,
                        token_number, reason, type, status, notes)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Scheduled', %s)
                    """
                    params = (
                        int(p_dropdown.value), int(d_dropdown.value), rec_id,
                        appt_date.value, appt_time.value, token_value,
                        visit_reason.value, appt_type.value, internal_notes.value
                    )

                    if execute_query(query, params):
                        doctor_fee_data = get_query_data(
                            "SELECT consultation_fee FROM Doctor WHERE doctor_id = %s",
                            (d_dropdown.value,)
                        )
                        consult_fee = float(doctor_fee_data[0]['consultation_fee']) if doctor_fee_data else 0.0

                        create_invoice_and_item(
                            patient_id=p_dropdown.value,
                            generated_by=rec_id,
                            admission_id=None,
                            item_type="Consultation",
                            description=f"Appointment consultation charge for Dr. {d_dropdown.value}",
                            quantity=1,
                            unit_price=consult_fee
                        )

                        show_snack("Appointment Successfully Added to Queue and billed.", ft.Colors.GREEN)
                        nav_to("book_appt")
                    else:
                        show_snack("Database Transaction Failed. Verify inputs.", ft.Colors.RED)

                except ValueError:
                    show_snack("Format Error: Date must be YYYY-MM-DD.", ft.Colors.RED)

            queue_data = get_query_data("""
                SELECT a.appointment_id, p.first_name, d.first_name as d_name, a.appointment_date, a.appointment_time, a.type, a.status 
                FROM Appointment a 
                JOIN Patient p ON a.patient_id = p.patient_id 
                JOIN Doctor d ON a.doctor_id = d.doctor_id 
                ORDER BY a.appointment_date DESC, a.appointment_time DESC
            """)
            
            q_rows = []
            for q in queue_data:
                status_val = q.get('status') or "Scheduled"
                type_val = q.get('type') or "OPD"
                status_color = ft.Colors.GREEN if status_val.lower() == 'completed' else ft.Colors.ORANGE
                
                q_rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(q['appointment_id']))), 
                            ft.DataCell(ft.Text(q['first_name'])), 
                            ft.DataCell(ft.Text(f"Dr. {q['d_name']}")), 
                            ft.DataCell(ft.Text(f"{q['appointment_date']} {q['appointment_time']}")),
                            ft.DataCell(ft.Text(type_val, weight="bold", color=ft.Colors.TEAL_700)),
                            ft.DataCell(
                                ft.Container(
                                    content=ft.Text(status_val.upper(), weight="bold", color=ft.Colors.WHITE, size=11), 
                                    bgcolor=status_color, 
                                    padding=5, 
                                    border_radius=5
                                )
                            )
                        ]
                    )
                )

            content_controls.append(
                ft.Column(
                    controls=[
                        ft.Text("Step 1: Patient Identification", weight="bold", color=ft.Colors.TEAL_900), 
                        ft.Row(controls=[p_dropdown, d_dropdown]),
                        ft.Text("Step 2: Scheduling Parameters", weight="bold", color=ft.Colors.TEAL_900), 
                        ft.Row(controls=[appt_date, appt_time, appt_type, token_num]), 
                        ft.Text("Step 3: Clinical Context", weight="bold", color=ft.Colors.TEAL_900),
                        ft.Row(controls=[visit_reason, internal_notes]),
                        ft.FilledButton(
                            "Verify Schedule & Commit Appointment", 
                            icon=ft.Icons.EVENT_AVAILABLE, 
                            style=rec_btn_style, 
                            on_click=execute_booking
                        ),
                        ft.Divider(height=40), 
                        ft.Text("Live Consultation Queue", weight="bold", size=20),
                        ft.DataTable(
                            columns=[
                                ft.DataColumn(ft.Text("Appt ID")), 
                                ft.DataColumn(ft.Text("Patient Name")), 
                                ft.DataColumn(ft.Text("Doctor Assigned")), 
                                ft.DataColumn(ft.Text("Date & Time")), 
                                ft.DataColumn(ft.Text("Type")), 
                                ft.DataColumn(ft.Text("Current Status"))
                            ], 
                            rows=q_rows
                        )
                    ]
                )
            )

        # =====================================================================
        # 5.9. MODULE: IPD ADMISSIONS & BED MANAGEMENT
        # =====================================================================
        elif tab == "admissions":
            patient_list = get_query_data("SELECT patient_id, first_name, last_name, registration_no FROM Patient")
            doctor_list = get_query_data("SELECT doctor_id, first_name, last_name FROM Doctor")
            
            # Complex Query: Only fetch beds that are physically Available
            bed_list = get_query_data("""
                SELECT b.bed_id, b.bed_number, r.room_number, w.ward_name 
                FROM Bed b 
                JOIN Room r ON b.room_id=r.room_id 
                JOIN Ward w ON r.ward_id = w.ward_id
                WHERE b.status='Available'
            """)
            
            p_dropdown = ft.Dropdown(
                label="Select Patient", 
                width=300, 
                options=[ft.dropdown.Option(key=str(p['patient_id']), text=f"{p['registration_no']} - {p['first_name']} {p['last_name']}") for p in patient_list]
            )
            d_dropdown = ft.Dropdown(
                label="Attending Physician", 
                width=300, 
                options=[ft.dropdown.Option(key=str(d['doctor_id']), text=f"Dr. {d['first_name']} {d['last_name']}") for d in doctor_list]
            )
            b_dropdown = ft.Dropdown(
                label="Assign Available Bed", 
                width=400, 
                options=[ft.dropdown.Option(key=str(b['bed_id']), text=f"Bed {b['bed_number']} | Room {b['room_number']} | {b['ward_name']}") for b in bed_list]
            )
            
            adm_date = ft.TextField(label="Admission Datestamp (YYYY-MM-DD HH:MM:SS)", width=350)
            adm_reason = ft.TextField(label="Medical Reason for Admission", width=550)

            def execute_admission(e):
                conn = get_db_connection()
                if not conn:
                    return
                def execute_admission(e):
                    conn = get_db_connection()
                    if not conn:
                        return

                    cursor = conn.cursor()

                    # ✅ FIX: ensure rec_id exists
                    rec_id = page.session.store.get("rec_id")
                    if not rec_id:
                        show_snack("Session expired. Please login again.", ft.Colors.RED)
                        return
                cursor = conn.cursor()
                try:
                    query1 = """
                        INSERT INTO Admission
                        (patient_id, doctor_id, bed_id, admission_date, reason, status)
                        VALUES (%s, %s, %s, %s, %s, 'Admitted')
                    """
                    params1 = (int(p_dropdown.value), int(d_dropdown.value), int(b_dropdown.value), adm_date.value, adm_reason.value)

                    query2 = "UPDATE Bed SET status = 'Occupied' WHERE bed_id = %s"
                    params2 = (int(b_dropdown.value),)

                    cursor.execute(query1, params1)
                    admission_id = cursor.lastrowid
                    cursor.execute(query2, params2)

                    room_data = get_query_data("""
                        SELECT r.daily_charge
                        FROM Bed b
                        JOIN Room r ON b.room_id = r.room_id
                        WHERE b.bed_id = %s
                    """, (b_dropdown.value,))

                    room_charge = float(room_data[0]['daily_charge']) if room_data else 0.0

                    invoice_no = f"INV-IPD-{int(datetime.datetime.now().timestamp())}"
                    cursor.execute("""
                        INSERT INTO Invoice (
                            invoice_number, patient_id, admission_id, generated_by,
                            subtotal, discount, tax, total_amount, paid_amount,
                            due_amount, payment_status, payment_mode, notes
                        ) VALUES (%s, %s, %s, %s, %s, 0, 0, %s, 0, %s, 'Unpaid', NULL, %s)
                    """, (
                        invoice_no, int(p_dropdown.value), admission_id, rec_id,
                        room_charge, room_charge, room_charge, "IPD admission charge"
                    ))
                    invoice_id = cursor.lastrowid

                    cursor.execute("""
                        INSERT INTO InvoiceItem
                        (invoice_id, item_type, description, quantity, unit_price, total_price)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        invoice_id, "Room",
                        f"Initial room charge for bed {b_dropdown.value}",
                        1, room_charge, room_charge
                    ))

                    conn.commit()
                    show_snack("IPD Admission processed, bed marked occupied, and bill created.", ft.Colors.GREEN)
                    nav_to("admissions")

                except Exception as e:
                    conn.rollback()
                    show_snack(f"Transaction Failed. {e}", ft.Colors.RED)
                finally:
                    cursor.close()
                    conn.close()

            adm_data = get_query_data("""
                SELECT a.admission_id, p.first_name, d.first_name as doc, b.bed_number, w.ward_name, a.admission_date, a.status 
                FROM Admission a 
                JOIN Patient p ON a.patient_id = p.patient_id 
                JOIN Doctor d ON a.doctor_id = d.doctor_id 
                JOIN Bed b ON a.bed_id = b.bed_id
                JOIN Room r ON b.room_id = r.room_id
                JOIN Ward w ON r.ward_id = w.ward_id
            """)
            
            if not adm_data: 
                content_controls.append(ft.Text("No active inpatient admissions found.", color=ft.Colors.GREY))
            else:
                a_rows = []
                for a in adm_data:
                    status_color = ft.Colors.ORANGE if a['status'] == 'Admitted' else ft.Colors.GREEN
                    a_rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(a['admission_id']))), 
                                ft.DataCell(ft.Text(a['first_name'])), 
                                ft.DataCell(ft.Text(f"Dr. {a['doc']}")), 
                                ft.DataCell(ft.Text(f"{a['ward_name']} / {a['bed_number']}")), 
                                ft.DataCell(ft.Text(str(a['admission_date']))), 
                                ft.DataCell(ft.Text(a['status'].upper(), color=status_color, weight="bold"))
                            ]
                        )
                    )
                
                content_controls.append(
                    ft.Column(
                        controls=[
                            ft.Text("Admit New Patient to Ward", weight="bold", color=ft.Colors.TEAL_900),
                            ft.Row(controls=[p_dropdown, d_dropdown, b_dropdown]), 
                            ft.Row(controls=[adm_date, adm_reason]),
                            ft.FilledButton(
                                "Process Inpatient Admission", 
                                icon=ft.Icons.BED, 
                                style=rec_btn_style, 
                                on_click=execute_admission
                            ), 
                            ft.Divider(height=40),
                            ft.Text("Active Inpatient Directory", weight="bold", size=20),
                            ft.DataTable(
                                columns=[
                                    ft.DataColumn(ft.Text("Adm ID")), 
                                    ft.DataColumn(ft.Text("Patient Name")), 
                                    ft.DataColumn(ft.Text("Attending Doctor")), 
                                    ft.DataColumn(ft.Text("Location")), 
                                    ft.DataColumn(ft.Text("Date Admitted")), 
                                    ft.DataColumn(ft.Text("Status"))
                                ], 
                                rows=a_rows
                            )
                        ]
                    )
                )

        # =====================================================================
        # 5.10. MODULE: FACILITY CONFIGURATION (Wards / Rooms / Beds)
        # =====================================================================
        elif tab == "rooms":
            # Ward Inputs
            w_name = ft.TextField(label="Ward Name", width=200)
            w_type = ft.Dropdown(
                label="Ward Type",
                width=200,
                options=[
                    ft.dropdown.Option("General"),
                    ft.dropdown.Option("ICU"),
                    ft.dropdown.Option("NICU"),
                    ft.dropdown.Option("Private"),
                    ft.dropdown.Option("Semi-Private"),  # ✅ FIX ADDED
                    ft.dropdown.Option("Emergency")
                ]
            )
            w_dept = ft.TextField(label="Dept ID", width=100)
            w_floor = ft.TextField(label="Floor", width=100)
            w_cap = ft.TextField(label="Capacity", width=100)
            
            def save_ward(e):
                query = "INSERT INTO Ward (ward_name, ward_type, dept_id, floor, capacity) VALUES (%s, %s, %s, %s, %s)"
                if execute_query(query, (w_name.value, w_type.value, w_dept.value, w_floor.value, w_cap.value)):
                    show_snack("Ward Generated Successfully!", ft.Colors.GREEN)
                    nav_to("rooms")
                else: 
                    show_snack("Error: Verify Department ID exists.", ft.Colors.RED)

            # Room Inputs
            r_num = ft.TextField(label="Room Number", width=200)
            r_ward_drop = ft.Dropdown(label="Select Existing Ward", width=250)
            r_type = ft.Dropdown(
                label="Room Configuration", 
                width=200, 
                options=[
                    ft.dropdown.Option("Single"), ft.dropdown.Option("Double"), ft.dropdown.Option("Multi")
                ]
            )
            r_charge = ft.TextField(label="Daily Charge (₹)", width=150)

            def save_room(e):
                query = "INSERT INTO Room (room_number, ward_id, room_type, daily_charge) VALUES (%s, %s, %s, %s)"
                if execute_query(query, (r_num.value, r_ward_drop.value, r_type.value, r_charge.value)):
                    show_snack("Room Attached to Ward Successfully!", ft.Colors.GREEN)
                    nav_to("rooms")
                else: 
                    show_snack("Error: Valid Ward must be selected.", ft.Colors.RED)

            # Bed Inputs
            b_num = ft.TextField(label="Bed Designation (e.g. B-01)", width=250)
            b_room_drop = ft.Dropdown(label="Select Existing Room", width=250)

            def save_bed(e):
                query = "INSERT INTO Bed (bed_number, room_id, status) VALUES (%s, %s, 'Available')"
                if execute_query(query, (b_num.value, b_room_drop.value)):
                    show_snack("Bed Deployed Successfully!", ft.Colors.GREEN)
                    nav_to("rooms")
                else: 
                    show_snack("Error: Valid Room must be selected.", ft.Colors.RED)

            facility_dlg = ft.AlertDialog(
                title=ft.Text("Facility Architecture Configuration", weight="bold"),
                content=ft.Container(
                    width=750, 
                    content=ft.Column(
                        controls=[
                            ft.Text("Step 1: Construct a Ward", weight="bold", color=ft.Colors.BLUE_900), 
                            ft.Row(controls=[w_name, w_type, w_dept, w_floor, w_cap]), 
                            ft.FilledButton("Construct Ward", style=admin_btn_style, on_click=save_ward), 
                            ft.Divider(),
                            
                            ft.Text("Step 2: Add Rooms to Ward", weight="bold", color=ft.Colors.BLUE_900), 
                            ft.Row(controls=[r_num, r_ward_drop, r_type, r_charge]), 
                            ft.FilledButton("Attach Room", style=admin_btn_style, on_click=save_room), 
                            ft.Divider(),
                            
                            ft.Text("Step 3: Deploy Beds to Room", weight="bold", color=ft.Colors.BLUE_900), 
                            ft.Row(controls=[b_num, b_room_drop]), 
                            ft.FilledButton("Deploy Bed", style=admin_btn_style, on_click=save_bed)
                        ], 
                        tight=True, 
                        scroll=ft.ScrollMode.AUTO
                    )
                ),
                actions=[
                    ft.TextButton(
                        "Close Architect", 
                        on_click=lambda e: setattr(facility_dlg, 'open', False) or page.update()
                    )
                ]
            )

            # Function to populate dropdowns dynamically
            def open_facility_architect(e):
                wards = get_query_data("SELECT ward_id, ward_name FROM Ward")
                r_ward_drop.options = [ft.dropdown.Option(key=str(w['ward_id']), text=f"ID: {w['ward_id']} - {w['ward_name']}") for w in wards]

                rooms = get_query_data("SELECT room_id, room_number FROM Room")
                b_room_drop.options = [ft.dropdown.Option(key=str(r['room_id']), text=f"ID: {r['room_id']} - Room {r['room_number']}") for r in rooms]

                page.overlay.append(facility_dlg)
                facility_dlg.open = True
                page.update()

            content_controls.append(
                ft.FilledButton(
                    "Open Architecture Configurator", 
                    icon=ft.Icons.DOMAIN_ADD, 
                    style=admin_btn_style, 
                    on_click=open_facility_architect
                )
            )
            content_controls.append(ft.Divider())

            # Data Tables for Facilities
            ward_data = get_query_data("SELECT ward_id, ward_name, ward_type, capacity FROM Ward")
            if ward_data:
                w_rows = []
                for w in ward_data:
                    w_rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(w['ward_id']))), 
                                ft.DataCell(ft.Text(w['ward_name'])), 
                                ft.DataCell(ft.Text(w['ward_type'])), 
                                ft.DataCell(ft.Text(str(w['capacity'])))
                            ]
                        )
                    )
                
                content_controls.extend([
                    ft.Text("Constructed Wards Overview", weight="bold", size=20), 
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Ward ID")), 
                            ft.DataColumn(ft.Text("Ward Name")), 
                            ft.DataColumn(ft.Text("Classification")), 
                            ft.DataColumn(ft.Text("Total Capacity"))
                        ], 
                        rows=w_rows
                    ),
                    ft.Divider(height=30)
                ])

            bed_data = get_query_data("SELECT b.bed_id, b.bed_number, r.room_number, b.status FROM Bed b JOIN Room r ON b.room_id = r.room_id")
            if bed_data:
                b_rows = []
                for b in bed_data:
                    b_rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(b['bed_id']))), 
                                ft.DataCell(ft.Text(b['bed_number'])), 
                                ft.DataCell(ft.Text(b['room_number'])), 
                                ft.DataCell(ft.Text(b['status'], color=ft.Colors.GREEN if b['status']=='Available' else ft.Colors.RED, weight="bold"))
                            ]
                        )
                    )

                content_controls.extend([
                    ft.Text("Real-Time Bed Matrix", weight="bold", size=20), 
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Bed Database ID")), 
                            ft.DataColumn(ft.Text("Bed Designation")), 
                            ft.DataColumn(ft.Text("Assigned Room")), 
                            ft.DataColumn(ft.Text("Occupancy Status"))
                        ], 
                        rows=b_rows
                    )
                ])
            else:
                content_controls.append(ft.Text("No beds currently exist in the database architecture.", color=ft.Colors.GREY))

        # =====================================================================
        # 5.11. MODULE: PHARMACY INVENTORY & BILLING (Dashboards)
        # =====================================================================
        elif tab == "meds":
            med_data = get_query_data("SELECT medicine_id, medicine_name, stock_quantity, unit_price, generic_name FROM Medicine")
            if not med_data: 
                content_controls.append(ft.Text("No medicines configured in Pharmacy Schema.", color=ft.Colors.GREY))
            else:
                m_rows = []
                for m in med_data:
                    stock_color = ft.Colors.RED if m['stock_quantity'] < 10 else ft.Colors.BLACK
                    m_rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(m['medicine_id']))), 
                                ft.DataCell(ft.Text(m['medicine_name'], weight="bold")), 
                                ft.DataCell(ft.Text(m['generic_name'] or "N/A")),
                                ft.DataCell(ft.Text(str(m['stock_quantity']), color=stock_color)), 
                                ft.DataCell(ft.Text(f"₹{m['unit_price']}"))
                            ]
                        )
                    )
                
                content_controls.extend([
                    ft.Text("Central Pharmacy Repository", weight="bold", size=20),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("ID")), 
                            ft.DataColumn(ft.Text("Medicine Brand Name")), 
                            ft.DataColumn(ft.Text("Generic Name")), 
                            ft.DataColumn(ft.Text("Available Stock")), 
                            ft.DataColumn(ft.Text("Unit Price"))
                        ], 
                        rows=m_rows
                    )
                ])

        elif tab in ["billing", "rec_billing"]:
            bill_data = get_query_data("SELECT i.invoice_id, i.invoice_number, p.first_name, p.last_name, i.total_amount, i.payment_status, i.invoice_date FROM Invoice i JOIN Patient p ON i.patient_id = p.patient_id")
            if not bill_data: 
                content_controls.append(ft.Text("No financial invoices found in the database.", color=ft.Colors.GREY))
            else:
                bill_rows = []
                for b in bill_data:
                    status_color = ft.Colors.GREEN if b['payment_status'] == 'Paid' else ft.Colors.RED
                    bill_rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(b['invoice_number']))), 
                                ft.DataCell(ft.Text(f"{b['first_name']} {b['last_name']}")), 
                                ft.DataCell(ft.Text(str(b['invoice_date']).split()[0])),
                                ft.DataCell(ft.Text(f"₹{b['total_amount']}")), 
                                ft.DataCell(ft.Text(b['payment_status'].upper(), weight="bold", color=status_color))
                            ]
                        )
                    )
                
                content_controls.extend([
                    ft.Text("Global Financial Transactions", weight="bold", size=20),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Invoice Num")), 
                            ft.DataColumn(ft.Text("Patient Name")), 
                            ft.DataColumn(ft.Text("Generated Date")), 
                            ft.DataColumn(ft.Text("Total Due")), 
                            ft.DataColumn(ft.Text("Settlement Status"))
                        ], 
                        rows=bill_rows
                    )
                ])

        # Return the entirely assembled View structure
        return ft.View(
            route="/dashboard",
            bgcolor=ft.Colors.GREY_50,
            controls=[
                ft.Row(
                    expand=True, 
                    spacing=0,
                    controls=[
                        sidebar, 
                        ft.Container(
                            expand=True, 
                            padding=40, 
                            content=ft.Column(
                                controls=content_controls, 
                                scroll=ft.ScrollMode.AUTO
                            )
                        )
                    ]
                )
            ]
        )
    def create_invoice_and_item(patient_id, generated_by, item_type, description, quantity, unit_price, admission_id=None):
        conn = get_db_connection()
        if not conn:
            return None

        cursor = conn.cursor()
        try:
            invoice_no = f"INV-{int(datetime.datetime.now().timestamp())}"
            qty = int(quantity)
            price = float(unit_price)
            subtotal = qty * price

            cursor.execute("""
                INSERT INTO Invoice (
                    invoice_number, patient_id, admission_id, generated_by,
                    subtotal, discount, tax, total_amount, paid_amount,
                    due_amount, payment_status, payment_mode, notes
                ) VALUES (%s, %s, %s, %s, %s, 0, 0, %s, 0, %s, 'Unpaid', NULL, %s)
            """, (
                invoice_no, int(patient_id), admission_id, generated_by,
                subtotal, subtotal, subtotal, description
            ))
            invoice_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO InvoiceItem (
                    invoice_id, item_type, description, quantity, unit_price, total_price
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (invoice_id, item_type, description, qty, price, subtotal))

            conn.commit()
            return invoice_id
        except Exception as e:
            conn.rollback()
            print(f"Invoice Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    # =====================================================================
    # 6. STARTUP EXECUTION ENGINE
    # =====================================================================
    page.views.clear()
    page.views.append(login_view())
    page.update()

if __name__ == "__main__":
    ft.run(main)