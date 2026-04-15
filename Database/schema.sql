-- Active: 1772286975086@@127.0.0.1@3306@hospital
create DATABASE hospital;
USE hospital; 

----------------------------------SYSTEM TABLES----------------------------------
--1.Department
CREATE TABLE Department (
    dept_id        INT PRIMARY KEY AUTO_INCREMENT,
    dept_name      VARCHAR(100) NOT NULL,          
    dept_code      VARCHAR(10)  UNIQUE NOT NULL,
    floor_number   INT,
    wing           VARCHAR(20),                    
    head_doctor_id INT, 
    phone_ext      VARCHAR(10),
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--2.Role
CREATE TABLE Role (
    role_id   INT PRIMARY KEY AUTO_INCREMENT,
    role_name VARCHAR(50) UNIQUE NOT NULL
);

--3.USERS
CREATE TABLE Users (
    user_id       INT PRIMARY KEY AUTO_INCREMENT,
    username      VARCHAR(50)  UNIQUE NOT NULL,
    u_password    VARCHAR(255) NOT NULL,
    email         VARCHAR(100) UNIQUE NOT NULL,
    role_id       INT NOT NULL,
    is_active     BOOLEAN DEFAULT TRUE,
    last_login    DATETIME,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES Role(role_id)
);

---------------------------------STAFF TABLES----------------------------------

--4. ADMIN

CREATE TABLE Admin (
    admin_id     INT PRIMARY KEY AUTO_INCREMENT,
    user_id      INT UNIQUE NOT NULL,
    first_name   VARCHAR(50) NOT NULL,
    last_name    VARCHAR(50) NOT NULL,
    phone        VARCHAR(15),
    employee_id  VARCHAR(20) UNIQUE,
    access_level ENUM('super','standard') DEFAULT 'standard',
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- 5. DOCTOR
CREATE TABLE Doctor (
    doctor_id        INT PRIMARY KEY AUTO_INCREMENT,
    user_id          INT UNIQUE NOT NULL,
    first_name       VARCHAR(50) NOT NULL,
    last_name        VARCHAR(50) NOT NULL,
    gender           ENUM('Male','Female','Other'),
    date_of_birth    DATE,
    phone            VARCHAR(15),
    email            VARCHAR(100),
    specialization   VARCHAR(100),            
    qualification    VARCHAR(200),            
    license_number   VARCHAR(50) UNIQUE,
    experience_years INT,
    dept_id          INT,
    consultation_fee DECIMAL(8,2),
    shift            ENUM('Morning','Evening','Night','Rotating'),
    joining_date     DATE,
    blood_group      VARCHAR(5),
    address          TEXT,
    photo_url        VARCHAR(255),
    FOREIGN KEY (user_id)  REFERENCES Users(user_id),
    FOREIGN KEY (dept_id)  REFERENCES Department(dept_id)
);
--- CIRCULAR DEPENDENCY
ALTER TABLE Department ADD CONSTRAINT fk_dept_head FOREIGN KEY (head_doctor_id) REFERENCES Doctor(doctor_id);

-- 6. DOCTOR AVAILABILITY 
CREATE TABLE DoctorAvailability (
    doctor_id   INT NOT NULL,
    day_of_week ENUM('Mon','Tue','Wed','Thu','Fri','Sat','Sun') NOT NULL,
    PRIMARY KEY (doctor_id, day_of_week),
    FOREIGN KEY (doctor_id) REFERENCES Doctor(doctor_id)
);

-- 7. RECEPTIONIST
CREATE TABLE Receptionist (
    receptionist_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id         INT UNIQUE NOT NULL,
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    gender          ENUM('Male','Female','Other'),
    phone           VARCHAR(15),
    employee_id     VARCHAR(20) UNIQUE,
    shift           ENUM('Morning','Evening','Night'),
    counter_number  INT,
    joining_date    DATE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

---------------------------------------PATIENT & WARDS TABLES----------------------------------

-- 8. PATIENT DETAILS
CREATE TABLE Patient (
    patient_id              INT PRIMARY KEY AUTO_INCREMENT,
    user_id                 INT UNIQUE,               
    registration_no         VARCHAR(20) UNIQUE NOT NULL,
    first_name              VARCHAR(50) NOT NULL,
    last_name               VARCHAR(50) NOT NULL,
    gender                  ENUM('Male','Female','Other'),
    date_of_birth           DATE,
    blood_group             VARCHAR(5),
    phone                   VARCHAR(15),
    email                   VARCHAR(100),
    address                 TEXT,
    city                    VARCHAR(50),
    state                   VARCHAR(50),
    pincode                 VARCHAR(10),
    emergency_contact_name  VARCHAR(100),
    emergency_contact_phone VARCHAR(15),
    emergency_contact_rel   VARCHAR(30),
    insurance_provider      VARCHAR(100),
    insurance_policy_no     VARCHAR(50),
    registered_by           INT,                      
    registered_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)       REFERENCES Users(user_id),
    FOREIGN KEY (registered_by) REFERENCES Receptionist(receptionist_id)
);

-- 9. MEDICAL HISTORY & ALLERGIES
CREATE TABLE MedicalHistory (
    history_id     INT PRIMARY KEY AUTO_INCREMENT,
    patient_id     INT NOT NULL,
    condition_name VARCHAR(200),
    diagnosed_date DATE,
    status         ENUM('Active','Resolved','Chronic'),
    notes          TEXT,
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id)
);

CREATE TABLE Allergy (
    allergy_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    allergen   VARCHAR(100),         
    reaction   VARCHAR(200),
    severity   ENUM('Mild','Moderate','Severe'),
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id)
);

-- 10. WARDS, ROOMS, BEDS
CREATE TABLE Ward (
    ward_id   INT PRIMARY KEY AUTO_INCREMENT,
    ward_name VARCHAR(50),
    ward_type ENUM('General','ICU','NICU','Private','Semi-Private','Emergency'),
    dept_id   INT,
    floor     INT,
    capacity  INT,
    FOREIGN KEY (dept_id) REFERENCES Department(dept_id)
);

CREATE TABLE Room (
    room_id      INT PRIMARY KEY AUTO_INCREMENT,
    room_number  VARCHAR(10) UNIQUE NOT NULL,
    ward_id      INT,
    room_type    ENUM('Single','Double','Multi'),
    ac           BOOLEAN DEFAULT FALSE,
    daily_charge DECIMAL(8,2),
    FOREIGN KEY (ward_id) REFERENCES Ward(ward_id)
);

CREATE TABLE Bed (
    bed_id     INT PRIMARY KEY AUTO_INCREMENT,
    bed_number VARCHAR(10) NOT NULL,
    room_id    INT,
    status     ENUM('Available','Occupied','Under Maintenance') DEFAULT 'Available',
    FOREIGN KEY (room_id) REFERENCES Room(room_id)
);

-----------------------------------APPOINTMENTS--------------------
-- 11. APPOINTMENTS
CREATE TABLE Appointment (
    appointment_id   INT PRIMARY KEY AUTO_INCREMENT,
    patient_id       INT NOT NULL,
    doctor_id        INT NOT NULL,
    receptionist_id  INT,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    token_number     INT,
    reason           TEXT,
    type             ENUM('OPD','IPD','Emergency','Follow-up','Online'),
    status           ENUM('Scheduled','Confirmed','Cancelled','Completed','No-Show') DEFAULT 'Scheduled',
    notes            TEXT,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id)      REFERENCES Patient(patient_id),
    FOREIGN KEY (doctor_id)       REFERENCES Doctor(doctor_id),
    FOREIGN KEY (receptionist_id) REFERENCES Receptionist(receptionist_id)
);

-- 12. ADMISSIONS (IPD)
CREATE TABLE Admission (
    admission_id    INT PRIMARY KEY AUTO_INCREMENT,
    patient_id      INT NOT NULL,
    doctor_id       INT NOT NULL,
    bed_id          INT NOT NULL,
    admission_date  DATETIME NOT NULL,
    discharge_date  DATETIME,
    reason          TEXT,
    diagnosis       TEXT,
    status          ENUM('Admitted','Discharged','Transferred','LAMA') DEFAULT 'Admitted',
    discharge_notes TEXT,
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
    FOREIGN KEY (doctor_id)  REFERENCES Doctor(doctor_id),
    FOREIGN KEY (bed_id)     REFERENCES Bed(bed_id)
);

-- 13. VITAL SIGNS
CREATE TABLE VitalSigns (
    vital_id         INT PRIMARY KEY AUTO_INCREMENT,
    patient_id       INT NOT NULL,
    recorded_by      INT,                         
    recorded_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    temperature      DECIMAL(4,1),                
    blood_pressure   VARCHAR(10),                 
    pulse_rate       INT,                         
    respiratory_rate INT,                         
    oxygen_saturation DECIMAL(5,2),               
    weight           DECIMAL(5,2),                
    height           DECIMAL(5,2),                
    bmi              DECIMAL(4,2),
    blood_sugar      DECIMAL(6,2),                
    notes            TEXT,
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
    FOREIGN KEY (recorded_by) REFERENCES Doctor(doctor_id)
);

-- 14. CONSULTATIONS
CREATE TABLE Consultation (
    consultation_id   INT PRIMARY KEY AUTO_INCREMENT,
    appointment_id    INT,
    patient_id        INT NOT NULL,
    doctor_id         INT NOT NULL,
    consult_date      DATETIME DEFAULT CURRENT_TIMESTAMP,
    chief_complaint   TEXT,
    symptoms          TEXT,
    examination_notes TEXT,
    diagnosis         TEXT,
    follow_up_date    DATE,
    follow_up_notes   TEXT,
    FOREIGN KEY (appointment_id) REFERENCES Appointment(appointment_id),
    FOREIGN KEY (patient_id)     REFERENCES Patient(patient_id),
    FOREIGN KEY (doctor_id)      REFERENCES Doctor(doctor_id)
);


----------------------------------PHARMACY----------------------------------

-- 15. MEDICINE CATALOG
CREATE TABLE MedicineCategory (
    category_id   INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(100) UNIQUE NOT NULL 
);

CREATE TABLE Medicine (
    medicine_id           INT PRIMARY KEY AUTO_INCREMENT,
    medicine_name         VARCHAR(150) NOT NULL,
    generic_name          VARCHAR(150),
    brand_name            VARCHAR(150),
    category_id           INT,
    dosage_form           ENUM('Tablet','Capsule','Syrup','Injection','Cream','Drops','Inhaler','Patch','Powder','Suppository'),
    strength              VARCHAR(50),                 
    manufacturer          VARCHAR(100),
    unit_price            DECIMAL(10,2),
    stock_quantity        INT DEFAULT 0,
    reorder_level         INT DEFAULT 10,
    expiry_date           DATE,
    storage_condition     VARCHAR(100),               
    prescription_required BOOLEAN DEFAULT TRUE,
    hsn_code              VARCHAR(20),                 
    created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES MedicineCategory(category_id)
);

-- 16. PRESCRIPTIONS
CREATE TABLE Prescription (
    prescription_id INT PRIMARY KEY AUTO_INCREMENT,
    consultation_id INT,
    patient_id      INT NOT NULL,
    doctor_id       INT NOT NULL,
    prescribed_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    valid_till      DATE,
    notes           TEXT,
    FOREIGN KEY (consultation_id) REFERENCES Consultation(consultation_id),
    FOREIGN KEY (patient_id)      REFERENCES Patient(patient_id),
    FOREIGN KEY (doctor_id)       REFERENCES Doctor(doctor_id)
);

CREATE TABLE PrescriptionItem (
    item_id         INT PRIMARY KEY AUTO_INCREMENT,
    prescription_id INT NOT NULL,
    medicine_id     INT NOT NULL,
    dosage          VARCHAR(50),                 
    frequency       VARCHAR(50),                 
    duration_days   INT,
    route           ENUM('Oral','IV','IM','SC','Topical','Inhalation'),
    instructions    TEXT,                        
    FOREIGN KEY (prescription_id) REFERENCES Prescription(prescription_id),
    FOREIGN KEY (medicine_id)     REFERENCES Medicine(medicine_id)
);

-- 17. PHARMACY DISPENSING
CREATE TABLE Pharmacist (
    pharmacist_id  INT PRIMARY KEY AUTO_INCREMENT,
    user_id        INT UNIQUE NOT NULL,
    first_name     VARCHAR(50) NOT NULL,
    last_name      VARCHAR(50) NOT NULL,
    license_number VARCHAR(50) UNIQUE,
    phone          VARCHAR(15),
    shift          ENUM('Morning','Evening','Night'),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE PharmacyDispense (
    dispense_id     INT PRIMARY KEY AUTO_INCREMENT,
    prescription_id INT,
    patient_id      INT NOT NULL,
    pharmacist_id   INT NOT NULL,
    dispensed_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_amount    DECIMAL(10,2),
    payment_status  ENUM('Pending','Paid','Waived') DEFAULT 'Pending',
    FOREIGN KEY (prescription_id) REFERENCES Prescription(prescription_id),
    FOREIGN KEY (patient_id)      REFERENCES Patient(patient_id),
    FOREIGN KEY (pharmacist_id)   REFERENCES Pharmacist(pharmacist_id)
);

CREATE TABLE DispenseItem (
    dispense_item_id INT PRIMARY KEY AUTO_INCREMENT,
    dispense_id      INT NOT NULL,
    medicine_id      INT NOT NULL,
    quantity         INT,
    unit_price       DECIMAL(10,2),
    total_price      DECIMAL(10,2),
    FOREIGN KEY (dispense_id)  REFERENCES PharmacyDispense(dispense_id),
    FOREIGN KEY (medicine_id)  REFERENCES Medicine(medicine_id)
);

-----------------------------LABORATORY & IMAGING----------------------------------

-- 18. LAB CATALOG
CREATE TABLE LabTestCategory (
    test_cat_id   INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE LabTest (
    test_id            INT PRIMARY KEY AUTO_INCREMENT,
    test_name          VARCHAR(150) NOT NULL,
    test_code          VARCHAR(20) UNIQUE,
    test_cat_id        INT,
    description        TEXT,
    sample_type        VARCHAR(50),               
    sample_volume      VARCHAR(30),               
    normal_range       VARCHAR(200),
    unit               VARCHAR(30),
    turnaround_hours   INT,                       
    price              DECIMAL(8,2),
    equipment_required VARCHAR(200),
    FOREIGN KEY (test_cat_id) REFERENCES LabTestCategory(test_cat_id)
);

-- 19. LAB TECHNICIAN
CREATE TABLE LabTechnician (
    lab_tech_id    INT PRIMARY KEY AUTO_INCREMENT,
    user_id        INT UNIQUE NOT NULL,
    first_name     VARCHAR(50) NOT NULL,
    last_name      VARCHAR(50) NOT NULL,
    gender         ENUM('Male','Female','Other'),
    phone          VARCHAR(15),
    employee_id    VARCHAR(20) UNIQUE,
    qualification  VARCHAR(200),
    specialization VARCHAR(100),                 
    shift          ENUM('Morning','Evening','Night'),
    joining_date   DATE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- 20. LAB ORDERS & RESULTS
CREATE TABLE LabOrder (
    order_id        INT PRIMARY KEY AUTO_INCREMENT,
    patient_id      INT NOT NULL,
    doctor_id       INT NOT NULL,
    consultation_id INT,
    ordered_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    priority        ENUM('Routine','Urgent','STAT') DEFAULT 'Routine',
    status          ENUM('Ordered','Sample Collected','Processing','Completed','Cancelled') DEFAULT 'Ordered',
    notes           TEXT,
    FOREIGN KEY (patient_id)      REFERENCES Patient(patient_id),
    FOREIGN KEY (doctor_id)       REFERENCES Doctor(doctor_id),
    FOREIGN KEY (consultation_id) REFERENCES Consultation(consultation_id)
);

CREATE TABLE LabOrderItem (
    order_item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id      INT NOT NULL,
    test_id       INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES LabOrder(order_id),
    FOREIGN KEY (test_id)  REFERENCES LabTest(test_id)
);

CREATE TABLE LabResult (
    result_id           INT PRIMARY KEY AUTO_INCREMENT,
    order_item_id       INT NOT NULL,
    lab_tech_id         INT NOT NULL,
    sample_collected_at DATETIME,
    result_value        TEXT,                       
    unit                VARCHAR(30),
    normal_range        VARCHAR(200),
    status              ENUM('Normal','Abnormal','Critical') DEFAULT 'Normal',
    remarks             TEXT,
    verified_by         INT, -- FK Added for strict relational integrity
    reported_at         DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_item_id) REFERENCES LabOrderItem(order_item_id),
    FOREIGN KEY (lab_tech_id)   REFERENCES LabTechnician(lab_tech_id),
    FOREIGN KEY (verified_by)   REFERENCES Doctor(doctor_id) 
);

--------------------------------------BILLING & PAYMENTS----------------------------------

-- 21. INVOICES
CREATE TABLE Invoice (
    invoice_id     INT PRIMARY KEY AUTO_INCREMENT,
    invoice_number VARCHAR(20) UNIQUE NOT NULL,
    patient_id     INT NOT NULL,
    admission_id   INT,
    generated_by   INT,                        
    invoice_date   DATETIME DEFAULT CURRENT_TIMESTAMP,
    subtotal       DECIMAL(10,2),
    discount       DECIMAL(10,2) DEFAULT 0,
    tax            DECIMAL(10,2) DEFAULT 0,
    total_amount   DECIMAL(10,2),
    paid_amount    DECIMAL(10,2) DEFAULT 0,
    due_amount     DECIMAL(10,2),
    payment_status ENUM('Unpaid','Partial','Paid','Waived') DEFAULT 'Unpaid',
    payment_mode   ENUM('Cash','Card','UPI','Insurance','Cheque'),
    notes          TEXT,
    FOREIGN KEY (patient_id)   REFERENCES Patient(patient_id),
    FOREIGN KEY (admission_id) REFERENCES Admission(admission_id),
    FOREIGN KEY (generated_by) REFERENCES Receptionist(receptionist_id)
);

CREATE TABLE InvoiceItem (
    item_id      INT PRIMARY KEY AUTO_INCREMENT,
    invoice_id   INT NOT NULL,
    item_type    ENUM('Consultation','Lab Test','Medicine','Room','Procedure','Other'),
    description  VARCHAR(255),
    quantity     INT DEFAULT 1,
    unit_price   DECIMAL(10,2),
    total_price  DECIMAL(10,2),
    FOREIGN KEY (invoice_id) REFERENCES Invoice(invoice_id)
);

-- 22. STAFF SCHEDULE
CREATE TABLE StaffSchedule (
    schedule_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id     INT NOT NULL,
    role_id     INT NOT NULL,
    work_date   DATE NOT NULL,
    shift_start TIME,
    shift_end   TIME,
    status      ENUM('Scheduled','Present','Absent','Leave') DEFAULT 'Scheduled',
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (role_id) REFERENCES Role(role_id)
);

-- 23. AUDIT LOG (For Security Tracking)
CREATE TABLE AuditLog (
    log_id     BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id    INT,
    action     VARCHAR(100),                     
    table_name VARCHAR(100),
    record_id  INT,
    old_values JSON,
    new_values JSON,
    ip_address VARCHAR(45),
    logged_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);
