
-- HOSPITAL DATABASE 

USE hospital_database;


SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = '';

-- ─────────────────────────────────────────────
-- 1. ROLES
-- ─────────────────────────────────────────────
INSERT INTO Role (role_id, role_name) VALUES
(1, 'Admin'),
(2, 'Receptionist'),
(3, 'Doctor'),
(4, 'Patient'),
(5, 'Lab Technician'),
(6, 'Pharmacist');

-- ─────────────────────────────────────────────
-- 2. DEPARTMENTS
-- ─────────────────────────────────────────────
INSERT INTO Department (dept_id, dept_name, dept_code, floor_number, wing, phone_ext) VALUES
(1,  'General Medicine',           'GM',    1, 'East',  '1001'),
(2,  'Cardiology',                 'CARD',  2, 'West',  '2001'),
(3,  'Orthopedics',                'ORTH',  3, 'North', '3001'),
(4,  'Neurology',                  'NEURO', 3, 'West',  '3002'),
(5,  'Gynecology & Obstetrics',    'GYN',   2, 'South', '2002'),
(6,  'Pediatrics',                 'PEDS',  1, 'North', '1002'),
(7,  'Radiology',                  'RAD',   0, 'East',  '0001'),
(8,  'Pathology & Lab',            'PATH',  0, 'West',  '0002'),
(9,  'Emergency',                  'ER',    0, 'South', '0003'),
(10, 'Ophthalmology',              'OPTH',  2, 'East',  '2003'),
(11, 'Dermatology',                'DERM',  2, 'North', '2004'),
(12, 'ENT',                        'ENT',   2, 'South', '2005'),
(13, 'Psychiatry',                 'PSY',   4, 'West',  '4001'),
(14, 'Oncology',                   'ONC',   4, 'East',  '4002'),
(15, 'Urology',                    'URO',   3, 'South', '3003');

-- ─────────────────────────────────────────────
-- 3. USERS 
-- ────────────────────────────────────────────
INSERT INTO Users (user_id, username, u_password, email, role_id, is_active, last_login, created_at) VALUES
-- Admins
(1,  'admin_suresh',    'admin_suresh123', 'suresh.admin@apollo.com',        1, TRUE, '2024-04-10 08:00:00', '2023-06-01'),
(2,  'admin_meghna',    'admin_meghna123', 'meghna.admin@apollo.com',        1, TRUE, '2024-04-10 09:00:00', '2023-06-01'),
-- Receptionists
(3,  'recep_kavya',     'recep_kavya123',  'kavya.iyer@apollo.com',          2, TRUE, '2024-04-11 07:30:00', '2023-07-01'),
(4,  'recep_ananya',    'recep_ananya123', 'ananya.recep@apollo.com',        2, TRUE, '2024-04-11 07:45:00', '2023-07-01'),
(5,  'recep_rohit',     'recep_rohit123',  'rohit.desk@apollo.com',          2, TRUE, '2024-04-10 07:00:00', '2023-08-15'),
-- Doctors
(6,  'doc_ankit_mehta', 'doc_ankit_mehta123','ankit.mehta@apollo.com',       3, TRUE, '2024-04-11 08:30:00', '2023-06-15'),
(7,  'doc_sana_khan',   'doc_sana_khan123',  'sana.khan@apollo.com',         3, TRUE, '2024-04-11 09:00:00', '2023-06-15'),
(8,  'doc_raj_singh',   'doc_raj_singh123',  'raj.singh@apollo.com',         3, TRUE, '2024-04-10 08:00:00', '2023-06-15'),
(9,  'doc_leena_nair',  'doc_leena_nair123', 'leena.nair@apollo.com',        3, TRUE, '2024-04-11 10:00:00', '2023-07-01'),
(10, 'doc_pradeep_rao', 'doc_pradeep_rao123','pradeep.rao@apollo.com',       3, TRUE, '2024-04-10 09:30:00', '2023-07-01'),
(11, 'doc_fatima_ali',  'doc_fatima_ali123', 'fatima.ali@apollo.com',        3, TRUE, '2024-04-11 11:00:00', '2023-08-01'),
(12, 'doc_vikram_das',  'doc_vikram_das123', 'vikram.das@apollo.com',        3, TRUE, '2024-04-10 10:00:00', '2023-08-01'),
(13, 'doc_sunita_bose', 'doc_sunita_bose123','sunita.bose@apollo.com',       3, TRUE, '2024-04-11 08:00:00', '2023-09-01'),
(14, 'doc_arjun_patel', 'doc_arjun_patel123','arjun.patel@apollo.com',       3, TRUE, '2024-04-10 07:30:00', '2023-09-01'),
(15, 'doc_nisha_gupta', 'doc_nisha_gupta123','nisha.gupta@apollo.com',       3, TRUE, '2024-04-11 09:30:00', '2023-10-01'),
-- Lab Technicians
(16, 'lab_rahul_dev',   'lab_rahul_dev123',  'rahul.dev@apollo.com',         5, TRUE, '2024-04-11 07:00:00', '2023-07-15'),
(17, 'lab_pooja_iyer',  'lab_pooja_iyer123', 'pooja.iyer@apollo.com',        5, TRUE, '2024-04-11 07:15:00', '2023-07-15'),
(18, 'lab_santosh_r',   'lab_santosh_r123',  'santosh.r@apollo.com',         5, TRUE, '2024-04-10 06:00:00', '2023-08-01'),
-- Pharmacists
(19, 'pharma_meera',    'pharma_meera123',   'meera.joshi@apollo.com',       6, TRUE, '2024-04-11 08:00:00', '2023-07-01'),
(20, 'pharma_deepak',   'pharma_deepak123',  'deepak.pharma@apollo.com',     6, TRUE, '2024-04-11 14:00:00', '2023-08-15'),
-- Patients
(21, 'pt_ravi_sharma',  'pt_ravi_sharma123', 'ravi.sharma@gmail.com',        4, TRUE, '2024-04-08 10:00:00', '2024-01-15'),
(22, 'pt_priya_verma',  'pt_priya_verma123', 'priya.verma@gmail.com',        4, TRUE, '2024-04-09 11:00:00', '2024-02-01'),
(23, 'pt_amit_patel',   'pt_amit_patel123',  'amit.patel@gmail.com',         4, TRUE, '2024-03-20 09:00:00', '2024-01-20'),
(24, 'pt_sunita_rao',   'pt_sunita_rao123',  'sunita.rao@gmail.com',         4, TRUE, '2024-04-01 08:00:00', '2024-02-10'),
(25, 'pt_karan_bose',   'pt_karan_bose123',  'karan.bose@gmail.com',         4, TRUE, '2024-03-15 10:00:00', '2024-01-05');

-- ─────────────────────────────────────────────
-- 4. ADMIN
-- ─────────────────────────────────────────────
INSERT INTO Admin (admin_id, user_id, first_name, last_name, phone, employee_id, access_level) VALUES
(1, 1, 'Suresh',  'Kumar',   '9811100001', 'EMP-ADM-001', 'super'),
(2, 2, 'Meghna',  'Sharma',  '9811100002', 'EMP-ADM-002', 'standard');

-- ─────────────────────────────────────────────
-- 5. DOCTORS (1NF FIX: available_days removed)
-- ─────────────────────────────────────────────
INSERT INTO Doctor (doctor_id, user_id, first_name, last_name, gender, date_of_birth, phone, email, specialization, qualification, license_number, experience_years, dept_id, consultation_fee, shift, joining_date, blood_group, address) VALUES
(1,  6,  'Ankit',   'Mehta',   'Male',   '1978-04-12', '9811200001', 'ankit.mehta@apollo.com',   'Cardiologist',          'MBBS, MD (Cardiology), DM',             'MCI-CARD-12345', 18, 2,  800.00,  'Morning',  '2020-03-01', 'B+',  '14 Vasant Vihar, New Delhi'),
(2,  7,  'Sana',    'Khan',    'Female', '1983-09-22', '9811200002', 'sana.khan@apollo.com',     'Neurologist',           'MBBS, MD, DM (Neurology)',              'MCI-NEURO-23456',13, 4,  1000.00, 'Evening',  '2021-01-15', 'A+',  '22 Saket, New Delhi'),
(3,  8,  'Raj',     'Singh',   'Male',   '1975-06-08', '9811200003', 'raj.singh@apollo.com',     'Orthopedician',         'MBBS, MS (Orthopedics)',                'MCI-ORTH-34567', 20, 3,  700.00,  'Morning',  '2019-06-01', 'O+',  '8 Sector 15, Noida'),
(4,  9,  'Leena',   'Nair',    'Female', '1981-12-30', '9811200004', 'leena.nair@apollo.com',    'Gynecologist',          'MBBS, MS (OBG)',                        'MCI-GYN-45678',  15, 5,  900.00,  'Rotating', '2020-09-01', 'AB+', '5 Punjabi Bagh, New Delhi'),
(5,  10, 'Pradeep', 'Rao',     'Male',   '1970-03-17', '9811200005', 'pradeep.rao@apollo.com',   'General Physician',     'MBBS, MD (General Medicine)',           'MCI-GM-56789',   25, 1,  500.00,  'Morning',  '2018-01-10', 'O-',  '33 Lajpat Nagar, New Delhi'),
(6,  11, 'Fatima',  'Ali',     'Female', '1987-07-04', '9811200006', 'fatima.ali@apollo.com',    'Pediatrician',          'MBBS, MD (Pediatrics)',                 'MCI-PEDS-67890', 10, 6,  600.00,  'Morning',  '2022-03-15', 'A-',  '12 Green Park, New Delhi'),
(7,  12, 'Vikram',  'Das',     'Male',   '1979-11-25', '9811200007', 'vikram.das@apollo.com',    'Radiologist',           'MBBS, MD (Radiology)',                  'MCI-RAD-78901',  17, 7,  600.00,  'Morning',  '2020-07-01', 'B-',  '7 Dwarka Sector 6, New Delhi'),
(8,  13, 'Sunita',  'Bose',    'Female', '1985-02-14', '9811200008', 'sunita.bose@apollo.com',   'Dermatologist',         'MBBS, MD (Dermatology)',                'MCI-DERM-89012', 12, 11, 800.00,  'Evening',  '2021-08-01', 'AB-', '19 Rohini Sector 3, New Delhi'),
(9,  14, 'Arjun',   'Patel',   'Male',   '1982-08-19', '9811200009', 'arjun.patel@apollo.com',   'ENT Specialist',        'MBBS, MS (ENT)',                        'MCI-ENT-90123',  14, 12, 700.00,  'Morning',  '2020-04-01', 'O+',  '3 Karol Bagh, New Delhi'),
(10, 15, 'Nisha',   'Gupta',   'Female', '1988-05-11', '9811200010', 'nisha.gupta@apollo.com',   'Psychiatrist',          'MBBS, MD (Psychiatry)',                 'MCI-PSY-01234',  9,  13, 1200.00, 'Evening',  '2022-11-01', 'B+',  '45 Pitampura, New Delhi');
 -- Update department heads
UPDATE Department SET head_doctor_id = 5 WHERE dept_id = 1;
UPDATE Department SET head_doctor_id = 1 WHERE dept_id = 2;
UPDATE Department SET head_doctor_id = 3 WHERE dept_id = 3;
UPDATE Department SET head_doctor_id = 2 WHERE dept_id = 4;
UPDATE Department SET head_doctor_id = 4 WHERE dept_id = 5;
UPDATE Department SET head_doctor_id = 6 WHERE dept_id = 6;
UPDATE Department SET head_doctor_id = 7 WHERE dept_id = 7;
UPDATE Department SET head_doctor_id = 8 WHERE dept_id = 11;
UPDATE Department SET head_doctor_id = 9 WHERE dept_id = 12;
UPDATE Department SET head_doctor_id = 10 WHERE dept_id = 13;

-- ─────────────────────────────────────────────
-- 5B. DOCTOR AVAILABILITY (
-- ─────────────────────────────────────────────
INSERT INTO DoctorAvailability (doctor_id, day_of_week) VALUES
(1, 'Mon'), (1, 'Tue'), (1, 'Wed'), (1, 'Thu'), (1, 'Fri'),
(2, 'Mon'), (2, 'Tue'), (2, 'Thu'), (2, 'Fri'), (2, 'Sat'),
(3, 'Mon'), (3, 'Wed'), (3, 'Fri'), (3, 'Sat'),
(4, 'Mon'), (4, 'Tue'), (4, 'Wed'), (4, 'Thu'), (4, 'Fri'), (4, 'Sat'),
(5, 'Mon'), (5, 'Tue'), (5, 'Wed'), (5, 'Thu'), (5, 'Fri'),
(6, 'Mon'), (6, 'Tue'), (6, 'Wed'), (6, 'Thu'), (6, 'Fri'),
(7, 'Mon'), (7, 'Tue'), (7, 'Wed'), (7, 'Thu'), (7, 'Fri'),
(8, 'Tue'), (8, 'Wed'), (8, 'Thu'), (8, 'Fri'), (8, 'Sat'),
(9, 'Mon'), (9, 'Tue'), (9, 'Wed'), (9, 'Fri'),
(10, 'Mon'), (10, 'Wed'), (10, 'Thu'), (10, 'Fri');

-- ─────────────────────────────────────────────
-- 6. RECEPTIONISTS
-- ─────────────────────────────────────────────
INSERT INTO Receptionist (receptionist_id, user_id, first_name, last_name, gender, phone, employee_id, shift, counter_number, joining_date) VALUES
(1, 3, 'Kavya',  'Iyer',    'Female', '9822100001', 'EMP-REC-001', 'Morning', 1, '2023-07-01'),
(2, 4, 'Ananya', 'Sharma',  'Female', '9822100002', 'EMP-REC-002', 'Evening', 2, '2023-07-01'),
(3, 5, 'Rohit',  'Verma',   'Male',   '9822100003', 'EMP-REC-003', 'Morning', 3, '2023-08-15');

-- ─────────────────────────────────────────────
-- 7. PATIENTS 
-- ─────────────────────────────────────────────
INSERT INTO Patient (patient_id, user_id, registration_no, first_name, last_name, gender, date_of_birth, blood_group, phone, email, address, city, state, pincode, emergency_contact_name, emergency_contact_phone, emergency_contact_rel, insurance_provider, insurance_policy_no, registered_by, registered_at) VALUES
(1,  21, 'APL-2024-0001', 'Ravi',        'Sharma',      'Male',   '1982-06-15', 'B+',  '9876500001', 'ravi.sharma@gmail.com',      '12 Main Street, Lajpat Nagar',       'New Delhi',  'Delhi',        '110024', 'Sunita Sharma',    '9876500099', 'Wife',        'Star Health',   'SH-POL-2892341',  1, '2024-01-15 09:30:00'),
(2,  22, 'APL-2024-0002', 'Priya',       'Verma',       'Female', '1990-11-20', 'A+',  '9123400001', 'priya.verma@gmail.com',      '45 Sector 18, Noida',                'Noida',      'Uttar Pradesh','201301', 'Raj Verma',        '9123400099', 'Husband',     'HDFC Ergo',     'HE-POL-7654321',  1, '2024-02-01 10:15:00'),
(3,  23, 'APL-2024-0003', 'Amit',        'Patel',       'Male',   '1969-02-28', 'O+',  '9765400001', 'amit.patel@gmail.com',       '22 DLF Phase 2',                     'Gurgaon',    'Haryana',      '122002', 'Rita Patel',       '9765400099', 'Wife',        'HDFC Ergo',     'HE-POL-1122334',  2, '2024-01-20 11:00:00'),
(4,  24, 'APL-2024-0004', 'Sunita',      'Rao',         'Female', '1995-03-10', 'AB+', '8888800001', 'sunita.rao@gmail.com',       'B-12 Rajouri Garden',                'New Delhi',  'Delhi',        '110027', 'Ramesh Rao',       '8888800099', 'Father',      'Max Bupa',      'MB-POL-9988776',  1, '2024-02-10 08:45:00'),
(5,  25, 'APL-2024-0005', 'Karan',       'Bose',        'Male',   '1957-08-22', 'O-',  '7777700001', 'karan.bose@gmail.com',       '7 Park Street',                      'Kolkata',    'West Bengal',  '700016', 'Meena Bose',       '7777700099', 'Wife',        'LIC Health',    'LIC-POL-5566778', 3, '2024-01-05 10:00:00'),
(6,  NULL,'APL-2024-0006', 'Deepa',      'Krishnan',    'Female', '1988-07-14', 'A-',  '9090900001', 'deepa.krishnan@yahoo.com',   '8 Anna Nagar',                       'Chennai',    'Tamil Nadu',   '600040', 'Suresh Krishnan',  '9090900099', 'Husband',     '',              '',                2, '2024-02-20 09:00:00'),
(7,  NULL,'APL-2024-0007', 'Mohammed',   'Iqbal',       'Male',   '2010-05-05', 'B+',  '9191900001', 'iqbal.family@gmail.com',     '15 Zakir Nagar',                     'New Delhi',  'Delhi',        '110025', 'Salma Iqbal',      '9191900099', 'Mother',      'Oriental Ins',  'OI-POL-3344556',  1, '2024-03-01 10:30:00'),
(8,  NULL,'APL-2024-0008', 'Geeta',      'Mishra',      'Female', '1950-12-01', 'O+',  '9292900001', 'geeta.mishra@gmail.com',     '3 Shyam Nagar',                      'Kanpur',     'Uttar Pradesh','208013', 'Rakesh Mishra',    '9292900099', 'Son',         'New India Ins', 'NI-POL-6677889',  3, '2024-03-05 11:15:00'),
(9,  NULL,'APL-2024-0009', 'Siddharth',  'Malhotra',    'Male',   '1993-04-18', 'AB-', '9393900001', 'sid.malhotra@outlook.com',   '20 Connaught Place',                 'New Delhi',  'Delhi',        '110001', 'Anjali Malhotra',  '9393900099', 'Sister',      'Religare',      'RG-POL-7788990',  1, '2024-03-10 09:45:00'),
(10, NULL,'APL-2024-0010', 'Lakshmi',    'Venkatesh',   'Female', '1978-09-25', 'B-',  '9494900001', 'lakshmi.v@gmail.com',        '11 Indira Nagar',                    'Bangalore',  'Karnataka',    '560038', 'Venkat Raman',     '9494900099', 'Husband',     'United India',  'UI-POL-8899001',  2, '2024-03-12 08:30:00'),
(11, NULL,'APL-2024-0011', 'Rahul',      'Joshi',       'Male',   '1985-01-30', 'A+',  '9595900001', 'rahul.joshi@gmail.com',      '55 Banjara Hills',                   'Hyderabad',  'Telangana',    '500034', 'Priti Joshi',      '9595900099', 'Wife',        'Apollo Munich', 'AM-POL-9900112',  1, '2024-03-15 10:00:00'),
(12, NULL,'APL-2024-0012', 'Anita',      'Desai',       'Female', '2020-08-08', 'O+',  '9696900001', 'anita.mother@gmail.com',     '9 Civil Lines',                      'Allahabad',  'Uttar Pradesh','211001', 'Sunil Desai',      '9696900099', 'Father',      '',              '',                3, '2024-03-18 09:15:00'),
(13, NULL,'APL-2024-0013', 'Vijay',      'Nambiar',     'Male',   '1960-03-14', 'B+',  '9797900001', 'vijay.nambiar@gmail.com',    '6 Marine Drive',                     'Mumbai',     'Maharashtra',  '400002', 'Usha Nambiar',     '9797900099', 'Wife',        'Star Health',   'SH-POL-1023456',  2, '2024-03-20 11:00:00'),
(14, NULL,'APL-2024-0014', 'Shreya',     'Agarwal',     'Female', '2001-06-22', 'AB+', '9898900001', 'shreya.agarwal@gmail.com',   '34 MG Road',                         'Pune',       'Maharashtra',  '411001', 'Mohan Agarwal',    '9898900099', 'Father',      'Bajaj Allianz', 'BA-POL-2134567',  1, '2024-03-22 08:00:00'),
(15, NULL,'APL-2024-0015', 'Harpreet',   'Singh',       'Male',   '1972-11-08', 'A-',  '9999900001', 'harpreet.singh@gmail.com',   '100 Model Town',                     'Ludhiana',   'Punjab',       '141002', 'Gurpreet Kaur',    '9999900099', 'Wife',        'National Ins',  'NA-POL-3245678',  2, '2024-03-25 10:30:00');

-- ─────────────────────────────────────────────
-- 8. MEDICAL HISTORY
-- ─────────────────────────────────────────────
INSERT INTO MedicalHistory (history_id, patient_id, condition_name, diagnosed_date, status, notes) VALUES
(1,  1,  'Hypertension (Stage 2)',            '2018-05-10', 'Chronic',  'BP consistently 150/95. On Amlodipine + Telmisartan.'),
(2,  1,  'Type 2 Diabetes Mellitus',          '2019-08-22', 'Chronic',  'HbA1c 7.8%. On Metformin 1000mg BD.'),
(3,  2,  'Migraine with Aura',                '2020-03-15', 'Chronic',  'Frequency: 3-4 episodes/month. On Topiramate prophylaxis.'),
(4,  3,  'Osteoarthritis - Bilateral Knee',   '2021-01-08', 'Chronic',  'Grade III changes bilateral. Physiotherapy ongoing.'),
(5,  3,  'Hypercholesterolemia',              '2019-06-20', 'Active',   'LDL 168 mg/dL. On Atorvastatin 40mg.'),
(6,  4,  'Iron Deficiency Anemia',            '2023-11-10', 'Resolved', 'Hb corrected to 12.5 g/dL after 3 months iron therapy.'),
(7,  5,  'Coronary Artery Disease',           '2020-04-18', 'Chronic',  'Triple vessel disease. CABG done 2020. On aspirin, statin, beta-blocker.'),
(8,  5,  'Hypertension',                      '2015-07-30', 'Chronic',  'Controlled. On Amlodipine 10mg.'),
(9,  6,  'Hypothyroidism',                    '2022-02-14', 'Active',   'TSH 8.2 mIU/L. On Levothyroxine 50mcg.'),
(10, 7,  'Acute Lymphoblastic Leukemia',      '2023-10-01', 'Active',   'Under chemotherapy protocol ALL-BFM 2019.'),
(11, 8,  'Osteoporosis',                      '2021-09-05', 'Chronic',  'T-score -2.8. On Calcium + Vit D + Alendronate.'),
(12, 8,  'Atrial Fibrillation',               '2022-03-20', 'Chronic',  'Paroxysmal AF. On Digoxin + Warfarin. INR maintained 2-3.'),
(13, 9,  'Peptic Ulcer Disease',              '2023-07-11', 'Resolved', 'H. pylori positive. Triple therapy completed.'),
(14, 10, 'PCOD (Polycystic Ovarian Disease)', '2020-11-25', 'Active',   'Irregular cycles. On OCP.'),
(15, 11, 'Bronchial Asthma',                  '2015-04-12', 'Chronic',  'Moderate persistent. On ICS + LABA inhaler.'),
(16, 13, 'Prostate Enlargement (BPH)',        '2021-08-18', 'Chronic',  'Prostate 48g. On Tamsulosin 0.4mg.'),
(17, 15, 'Ankylosing Spondylitis',            '2019-05-22', 'Chronic',  'HLA-B27 positive. On NSAIDs + physiotherapy.');

-- ─────────────────────────────────────────────
-- 9. ALLERGIES
-- ─────────────────────────────────────────────
INSERT INTO Allergy (allergy_id, patient_id, allergen, reaction, severity) VALUES
(1,  1,  'Penicillin',          'Urticaria, angioedema',              'Severe'),
(2,  1,  'Sulfonamides',        'Rash',                               'Mild'),
(3,  2,  'Aspirin / NSAIDs',    'Bronchospasm, nasal polyps',         'Severe'),
(4,  3,  'Shellfish',           'Urticaria',                          'Moderate'),
(5,  5,  'Streptokinase',       'Anaphylaxis (documented 2018)',      'Severe'),
(6,  6,  'Latex',               'Contact dermatitis',                 'Mild'),
(7,  8,  'Morphine',            'Excessive sedation, nausea',         'Moderate'),
(8,  9,  'Ibuprofen',           'Gastric irritation, hematemesis',    'Moderate'),
(9,  11, 'Dust mites',          'Bronchospasm',                       'Severe'),
(10, 13, 'Contrast dye (iodine)','Urticaria, BP drop',               'Severe');

-- ─────────────────────────────────────────────
-- 10. WARDS, ROOMS, BEDS
-- ─────────────────────────────────────────────
INSERT INTO Ward (ward_id, ward_name, ward_type, dept_id, floor, capacity) VALUES
(1,  'Cardiology Ward A',       'Private',     2,  2,  10),
(2,  'Cardiology ICU',          'ICU',         2,  2,  8),
(3,  'Ortho Ward B',            'General',     3,  3,  20),
(4,  'Neuro Ward C',            'Semi-Private',4,  3,  15),
(5,  'Maternity Ward',          'Private',     5,  2,  12),
(6,  'NICU',                    'NICU',        6,  1,  10),
(7,  'Pediatric Ward D',        'General',     6,  1,  20),
(8,  'Emergency Ward',          'Emergency',   9,  0,  30),
(9,  'General Ward E',          'General',     1,  1,  40),
(10, 'ICU General',             'ICU',         1,  1,  12);

INSERT INTO Room (room_id, room_number, ward_id, room_type, ac, daily_charge) VALUES
(1,  'C-101', 1,  'Single', TRUE,  4500.00),
(2,  'C-102', 1,  'Single', TRUE,  4500.00),
(3,  'C-103', 1,  'Double', TRUE,  3000.00),
(4,  'CI-01', 2,  'Single', TRUE,  8000.00),
(5,  'CI-02', 2,  'Single', TRUE,  8000.00),
(6,  'O-201', 3,  'Multi',  FALSE, 1200.00),
(7,  'O-202', 3,  'Double', FALSE, 1800.00),
(8,  'N-301', 4,  'Single', TRUE,  3500.00),
(9,  'N-302', 4,  'Double', TRUE,  2500.00),
(10, 'M-101', 5,  'Single', TRUE,  5000.00),
(11, 'M-102', 5,  'Double', TRUE,  3500.00),
(12, 'G-101', 9,  'Multi',  FALSE, 800.00),
(13, 'G-102', 9,  'Multi',  FALSE, 800.00),
(14, 'ER-01', 8,  'Single', TRUE,  2000.00),
(15, 'ICU-01',10, 'Single', TRUE,  10000.00);

INSERT INTO Bed (bed_id, bed_number, room_id, status) VALUES
(1,  'C-101-A', 1,  'Occupied'),
(2,  'C-102-A', 2,  'Available'),
(3,  'C-103-A', 3,  'Occupied'),
(4,  'C-103-B', 3,  'Available'),
(5,  'CI-01-A', 4,  'Occupied'),
(6,  'CI-02-A', 5,  'Available'),
(7,  'O-201-A', 6,  'Available'),
(8,  'O-201-B', 6,  'Occupied'),
(9,  'O-201-C', 6,  'Available'),
(10, 'O-202-A', 7,  'Occupied'),
(11, 'N-301-A', 8,  'Occupied'),
(12, 'N-302-A', 9,  'Available'),
(13, 'N-302-B', 9,  'Available'),
(14, 'M-101-A', 10, 'Available'),
(15, 'G-101-A', 12, 'Occupied'),
(16, 'G-101-B', 12, 'Occupied'),
(17, 'G-101-C', 12, 'Available'),
(18, 'ER-01-A', 14, 'Occupied'),
(19, 'ICU-01-A',15, 'Occupied'),
(20, 'ICU-01-B',15, 'Under Maintenance');

-- ─────────────────────────────────────────────
-- 11. APPOINTMENTS
-- ─────────────────────────────────────────────
INSERT INTO Appointment (appointment_id, patient_id, doctor_id, receptionist_id, appointment_date, appointment_time, token_number, reason, type, status, notes) VALUES
-- Past completed appointments
(1,  1,  1,  1, '2024-02-05', '09:00:00', 1,  'Chest pain on exertion, shortness of breath',   'OPD',       'Completed', 'ECG done. Stress test ordered.'),
(2,  3,  3,  2, '2024-02-06', '10:30:00', 2,  'Left knee pain, swelling',                      'OPD',       'Completed', 'X-ray done. Physio recommended.'),
(3,  5,  1,  1, '2024-02-08', '09:30:00', 3,  'Post-CABG follow-up, breathlessness',           'Follow-up', 'Completed', 'Stable. ECHO ordered.'),
(4,  2,  2,  1, '2024-02-10', '11:00:00', 1,  'Severe headache, visual disturbance',           'OPD',       'Completed', 'MRI Brain ordered.'),
(5,  6,  4,  2, '2024-02-12', '10:00:00', 2,  'Menstrual irregularity, weight gain',           'OPD',       'Completed', 'USG pelvis ordered. TSH done.'),
(6,  7,  6,  1, '2024-02-15', '09:00:00', 1,  'Fever, fatigue, bruising',                      'Emergency', 'Completed', 'CBC critical. Oncology referral.'),
(7,  8,  5,  3, '2024-02-18', '11:30:00', 3,  'Palpitations, dizziness',                       'OPD',       'Completed', 'ECG: AF. Cardiology referred.'),
(8,  9,  5,  1, '2024-02-20', '10:00:00', 4,  'Epigastric pain, heartburn',                    'OPD',       'Completed', 'H. pylori test positive. Triple therapy started.'),
(9,  10, 4,  2, '2024-02-22', '09:30:00', 2,  'Irregular periods, acne, hair loss',            'OPD',       'Completed', 'PCOD confirmed on USG.'),
(10, 11, 5,  1, '2024-02-25', '11:00:00', 5,  'Wheezing, breathlessness on exertion',          'OPD',       'Completed', 'PFT done. ICS/LABA started.'),
-- Recent appointments
(11, 1,  1,  1, '2024-04-01', '09:00:00', 1,  'BP poorly controlled, ankle swelling',          'Follow-up', 'Completed', 'BP: 160/100. Medication adjusted.'),
(12, 5,  1,  1, '2024-04-03', '09:30:00', 2,  'Chest heaviness, left arm pain',                'OPD',       'Completed', 'Troponin elevated. Admitted.'),
(13, 2,  2,  2, '2024-04-05', '10:00:00', 1,  'Follow up after MRI',                           'Follow-up', 'Completed', 'MRI: Cluster headache. Medication changed.'),
(14, 4,  4,  1, '2024-04-06', '11:00:00', 3,  'Anemia follow-up, fatigue',                     'Follow-up', 'Completed', 'Hb 11.8 g/dL. Continue iron.'),
(15, 8,  1,  3, '2024-04-07', '09:00:00', 1,  'Cardiology consult for AF',                     'Follow-up', 'Completed', 'INR 2.4. AF rate controlled.'),
-- Today's appointments
(16, 1,  1,  1, '2024-04-11', '09:00:00', 1,  'BP follow-up, diabetes review',                 'Follow-up', 'Completed', NULL),
(17, 2,  2,  1, '2024-04-11', '09:30:00', 2,  'Headache, nausea since 3 days',                 'OPD',       'Confirmed', NULL),
(18, 3,  3,  2, '2024-04-11', '10:00:00', 3,  'Right shoulder pain post-fall',                 'OPD',       'Waiting',   NULL),
(19, 4,  4,  1, '2024-04-11', '10:30:00', 4,  'Irregular periods, PCOD follow-up',             'Follow-up', 'Waiting',   NULL),
(20, 6,  5,  2, '2024-04-11', '11:00:00', 5,  'Thyroid follow-up',                             'Follow-up', 'Scheduled', NULL),
(21, 9,  5,  1, '2024-04-11', '11:30:00', 6,  'Stomach ulcer follow-up',                       'Follow-up', 'Scheduled', NULL),
(22, 11, 5,  3, '2024-04-11', '12:00:00', 7,  'Asthma review',                                 'Follow-up', 'Scheduled', NULL),
(23, 13, 5,  2, '2024-04-11', '14:00:00', 8,  'Prostate symptoms',                             'OPD',       'Scheduled', NULL),
(24, 14, 8,  1, '2024-04-11', '14:30:00', 1,  'Acne vulgaris, oily skin',                      'OPD',       'Scheduled', NULL),
(25, 15, 3,  2, '2024-04-11', '15:00:00', 2,  'Low back pain, stiffness',                      'OPD',       'Scheduled', NULL),
-- Future appointments
(26, 1,  1,  1, '2024-04-18', '09:00:00', 1,  'Monthly BP & DM review',                        'Follow-up', 'Scheduled', NULL),
(27, 7,  6,  1, '2024-04-12', '09:30:00', 2,  'Chemotherapy cycle 4',                          'IPD',       'Confirmed', NULL),
(28, 12, 6,  2, '2024-04-15', '10:00:00', 3,  'Child fever, cough',                            'OPD',       'Scheduled', NULL);

-- ─────────────────────────────────────────────
-- 12. ADMISSIONS
-- ─────────────────────────────────────────────
INSERT INTO Admission (admission_id, patient_id, doctor_id, bed_id, admission_date, discharge_date, reason, diagnosis, status, discharge_notes) VALUES
(1, 5,  1,  1,  '2024-04-03 14:30:00', NULL,                  'Acute chest pain, STEMI suspected',         'Non-ST Elevation MI (NSTEMI). Managed medically. PCI deferred.', 'Admitted', NULL),
(2, 7,  6,  15, '2024-03-01 11:00:00', NULL,                  'Fever, fatigue, leukocytosis',              'Acute Lymphoblastic Leukemia. Chemotherapy cycle 3 ongoing.',    'Admitted', NULL),
(3, 8,  1,  5,  '2024-03-20 09:00:00', NULL,                  'Rapid AF with hemodynamic compromise',      'Atrial Fibrillation with fast ventricular rate. Rate controlled.','Admitted', NULL),
(4, 2,  2,  11, '2024-03-15 16:00:00', '2024-03-20 11:00:00', 'Severe cluster headache, vomiting',         'Cluster Headache. MRI Brain normal.',                            'Discharged','Pain controlled. Discharge on oral medication. Follow-up 2 weeks.'),
(5, 11, 5,  19, '2024-03-25 22:00:00', '2024-03-28 10:00:00', 'Acute severe asthma, oxygen saturation 88%','Acute exacerbation of bronchial asthma.',                        'Discharged','Stabilized. SpO2 99% on room air. Discharge with inhaler + oral steroids.'),
(6, 4,  4,  14, '2024-02-05 10:00:00', '2024-02-08 11:00:00', 'Severe anemia, Hb 5.2 g/dL',                'Iron deficiency anemia. 2 units PRBC transfused.',               'Discharged','Hb post-transfusion 9.8 g/dL. Discharged on oral iron.');

-- ─────────────────────────────────────────────
-- 13. VITAL SIGNS
-- ─────────────────────────────────────────────
INSERT INTO VitalSigns (vital_id, patient_id, recorded_by, recorded_at, temperature, blood_pressure, pulse_rate, respiratory_rate, oxygen_saturation, weight, height, bmi, blood_sugar, notes) VALUES
(1,  1,  1,  '2024-04-11 09:15:00', 36.8, '158/96',  82,  18, 97.00, 88.5,  172.0, 29.9, 186.0, 'Pre-consultation vitals. BP elevated. FBS elevated.'),
(2,  2,  2,  '2024-04-11 09:35:00', 37.1, '118/76',  76,  17, 99.00, 62.0,  163.0, 23.3, 88.0,  'Vitals within normal limits.'),
(3,  3,  3,  '2024-04-11 10:05:00', 36.6, '130/85',  78,  16, 98.00, 95.0,  175.0, 31.0, 102.0, 'Mild hypertension. Overweight.'),
(4,  5,  1,  '2024-04-03 15:00:00', 37.4, '100/68',  104, 22, 93.00, 72.0,  168.0, 25.5, 110.0, 'CCU admission vitals. Tachycardia. Low SpO2.'),
(5,  5,  1,  '2024-04-10 08:00:00', 36.9, '118/74',  72,  16, 97.00, 72.0,  168.0, 25.5, 98.0,  'Improving. Day 7 CCU. BP stable.'),
(6,  7,  6,  '2024-03-01 11:30:00', 38.9, '102/70',  110, 24, 95.00, 28.5,  138.0, 14.9, 92.0,  'Fever at admission. Tachycardia. Pediatric patient.'),
(7,  8,  1,  '2024-03-20 09:30:00', 36.7, '108/72',  118, 20, 94.00, 58.0,  154.0, 24.5, 96.0,  'Rapid AF at admission.'),
(8,  8,  1,  '2024-04-11 08:30:00', 36.5, '128/82',  84,  16, 97.00, 58.0,  154.0, 24.5, 104.0, 'AF rate controlled. Stable on medication.'),
(9,  11, 5,  '2024-03-25 22:15:00', 37.2, '132/84',  112, 30, 88.00, 78.0,  178.0, 24.6, 94.0,  'Emergency admission. SpO2 critically low. Tachycardia. Tachypnea.'),
(10, 11, 5,  '2024-03-28 09:00:00', 36.8, '124/80',  78,  16, 99.00, 78.0,  178.0, 24.6, 90.0,  'Pre-discharge. Fully recovered.'),
(11, 4,  4,  '2024-04-11 10:35:00', 36.9, '112/70',  74,  16, 99.00, 58.0,  161.0, 22.4, 96.0,  'Routine OPD vitals. Normal.'),
(12, 9,  5,  '2024-04-11 11:35:00', 36.7, '120/78',  70,  15, 99.00, 74.0,  176.0, 23.9, 90.0,  'Normal vitals.'),
(13, 13, 5,  '2024-04-11 14:05:00', 36.8, '138/88',  80,  16, 98.00, 84.0,  170.0, 29.1, 108.0, 'Mildly elevated BP. Overweight.'),
(14, 15, 3,  '2024-04-11 15:05:00', 36.6, '126/80',  72,  16, 98.00, 82.0,  174.0, 27.1, 94.0,  'Normal vitals.');

-- ─────────────────────────────────────────────
-- 14. CONSULTATIONS
-- ─────────────────────────────────────────────
INSERT INTO Consultation (consultation_id, appointment_id, patient_id, doctor_id, consult_date, chief_complaint, symptoms, examination_notes, diagnosis, follow_up_date, follow_up_notes) VALUES
(1,  1,  1,  1,  '2024-02-05 09:20:00', 'Chest pain on exertion',             'Exertional chest pain, breathlessness climbing stairs, ankle swelling',              'BP: 162/98. Bilateral mild pitting edema. Heart sounds normal. No murmur.', 'Hypertensive heart disease. Rule out CAD.', '2024-04-01', 'Review after TMT and ECHO results.'),
(2,  2,  3,  3,  '2024-02-06 10:45:00', 'Left knee pain and swelling',        'Pain 3 months, morning stiffness 30 min, bilateral but L>R, crepitus',              'Left knee effusion present. Reduced ROM. Valgus deformity mild.', 'Osteoarthritis left knee Grade III.', '2024-04-11', 'Review after physiotherapy.'),
(3,  3,  5,  1,  '2024-02-08 09:45:00', 'Post-CABG breathlessness',           'Dyspnea on mild exertion. No chest pain. Mild ankle swelling.',                     'HR 88 irregular (AF). BP 118/78. Mild bilateral crepts at bases.', 'Post CABG, stable. Paroxysmal AF. Heart failure NYHA Class II.', '2024-04-03', 'ECHO follow-up.'),
(4,  4,  2,  2,  '2024-02-10 11:15:00', 'Severe headache with visual aura',   'Unilateral throbbing headache, photophobia, nausea, visual aura before attacks.',   'Neurological exam normal. Fundoscopy normal.', 'Migraine with aura. Tension type headache excluded.', '2024-04-05', 'MRI Brain review.'),
(5,  11, 1,  1,  '2024-04-01 09:15:00', 'BP poorly controlled',               'Ankle swelling, early morning headache, fatigue. DM also not controlled.',           'BP: 160/100. Both ankles edema 1+. FBS: 204 mg/dL.',              'Uncontrolled HTN + DM. Medication escalation needed.', '2024-04-18', 'BP and sugar review with reports.'),
(6,  12, 5,  1,  '2024-04-03 09:45:00', 'Chest heaviness radiating to jaw',   'Sudden onset, 30 min duration, associated sweating and nausea.',                     'BP: 98/64. PR: 108. ECG: ST depression V1-V4. Troponin-I: 2.8 ng/mL.', 'NSTEMI (Non-ST Elevation Myocardial Infarction). Admitted to CCU.', NULL, 'Admitted. Dual antiplatelet + LMWH + Statin + Beta-blocker.'),
(7,  13, 2,  2,  '2024-04-05 10:15:00', 'Headache follow-up',                 'MRI review. Pain slightly improved on new medication.',                              'MRI: No structural abnormality. No aneurysm.', 'Cluster headache confirmed. Good response to Verapamil.', '2024-05-05', 'Continue current medication. Review in 1 month.'),
(8,  16, 1,  1,  '2024-04-11 09:20:00', 'Routine BP and diabetes review',     'Feels better after dose adjustment. FBS home readings 140-160 mg/dL.',              'BP: 138/88. Ankles no edema. FBS: 148 mg/dL.',                    'HTN improved. DM partially controlled. HbA1c ordered.', '2024-04-18', 'HbA1c and lipid profile review.');

-- ─────────────────────────────────────────────
-- 15. MEDICINE CATEGORIES
-- ─────────────────────────────────────────────
INSERT INTO MedicineCategory (category_id, category_name) VALUES
(1,  'Antibiotic'),
(2,  'Analgesic / NSAID'),
(3,  'Antihypertensive'),
(4,  'Antidiabetic'),
(5,  'Antihistamine'),
(6,  'Antacid / PPI'),
(7,  'Cardiovascular'),
(8,  'Vitamin / Supplement'),
(9,  'Antipyretic'),
(10, 'Anticoagulant'),
(11, 'Bronchodilator'),
(12, 'Antidepressant / Psychiatry'),
(13, 'Corticosteroid'),
(14, 'Antiepileptic'),
(15, 'Antifungal'),
(16, 'Hormonal'),
(17, 'Diuretic'),
(18, 'Anticancer / Chemotherapy'),
(19, 'Ophthalmic'),
(20, 'Topical / Dermatological');

-- ─────────────────────────────────────────────
-- 16. MEDICINES
-- ─────────────────────────────────────────────
INSERT INTO Medicine (medicine_id, medicine_name, generic_name, brand_name, category_id, dosage_form, strength, manufacturer, unit_price, stock_quantity, reorder_level, expiry_date, storage_condition, prescription_required, hsn_code) VALUES
(1,  'Augmentin 625',       'Amoxicillin + Clavulanate', 'Augmentin',     1,  'Tablet',    '625mg',    'GSK',               28.00,  480,  50,  '2025-09-30', 'Room temperature',   TRUE,  '30049099'),
(2,  'Azithromycin 500',    'Azithromycin',              'Zithromax',     1,  'Tablet',    '500mg',    'Cipla',             24.50,  320,  40,  '2025-11-30', 'Room temperature',   TRUE,  '30049099'),
(3,  'Cefixime 200',        'Cefixime',                  'Taxim-O',       1,  'Tablet',    '200mg',    'Alkem',             32.00,  280,  40,  '2025-08-31', 'Room temperature',   TRUE,  '30049099'),
(4,  'Crocin 500',          'Paracetamol',               'Crocin',        9,  'Tablet',    '500mg',    'GSK',                3.50, 1500,  150, '2026-03-31', 'Room temperature',   FALSE, '30049099'),
(5,  'Combiflam',           'Ibuprofen + Paracetamol',   'Combiflam',     2,  'Tablet',    '400/325mg','Sanofi',             7.00,  900,  100, '2025-12-31', 'Room temperature',   FALSE, '30049099'),
(6,  'Diclofenac 50',       'Diclofenac Sodium',         'Voveran',       2,  'Tablet',    '50mg',     'Novartis',           8.50,  600,  80,  '2025-10-31', 'Room temperature',   FALSE, '30049099'),
(7,  'Amlodipine 5',        'Amlodipine Besylate',       'Norvasc',       3,  'Tablet',    '5mg',      'Pfizer',             5.00,  800,  80,  '2026-01-31', 'Room temperature',   TRUE,  '30049099'),
(8,  'Telmisartan 40',      'Telmisartan',               'Telma',         3,  'Tablet',    '40mg',     'Glenmark',          12.00,  650,  70,  '2025-11-30', 'Room temperature',   TRUE,  '30049099'),
(9,  'Atenolol 50',         'Atenolol',                  'Tenormin',      3,  'Tablet',    '50mg',     'AstraZeneca',        6.50,  550,  60,  '2025-09-30', 'Room temperature',   TRUE,  '30049099'),
(10, 'Furosemide 40',       'Furosemide',                'Lasix',         17, 'Tablet',    '40mg',     'Sanofi',             4.50,  400,  50,  '2025-08-31', 'Room temperature',   TRUE,  '30049099'),
(11, 'Metformin 500',       'Metformin HCl',             'Glycomet',      4,  'Tablet',    '500mg',    'USV',                4.50,  900,  90,  '2026-02-28', 'Room temperature',   TRUE,  '30049099'),
(12, 'Glimepiride 2',       'Glimepiride',               'Amaryl',        4,  'Tablet',    '2mg',      'Sanofi',            14.00,  420,  50,  '2025-10-31', 'Room temperature',   TRUE,  '30049099'),
(13, 'Insulin Glargine',    'Insulin Glargine',          'Lantus',        4,  'Injection', '100 IU/mL','Sanofi',           850.00,   80,  15,  '2024-12-31', 'Refrigerate 2-8°C',  TRUE,  '30042090'),
(14, 'Cetirizine 10',       'Cetirizine HCl',            'Zyrtec',        5,  'Tablet',    '10mg',     'UCB',                4.00,  500,  60,  '2025-12-31', 'Room temperature',   FALSE, '30049099'),
(15, 'Montelukast 10',      'Montelukast',               'Singulair',     11, 'Tablet',    '10mg',     'MSD',               38.00,  300,  40,  '2025-09-30', 'Room temperature',   TRUE,  '30049099'),
(16, 'Pantoprazole 40',     'Pantoprazole Sodium',       'Pantocid',      6,  'Tablet',    '40mg',     'Sun Pharma',         8.00,  700,  80,  '2025-11-30', 'Room temperature',   TRUE,  '30049099'),
(17, 'Omeprazole 20',       'Omeprazole',                'Omez',          6,  'Capsule',   '20mg',     'Dr Reddy',           7.50,  550,  70,  '2025-10-31', 'Room temperature',   TRUE,  '30049099'),
(18, 'Aspirin 75',          'Aspirin (Enteric Coated)',  'Ecosprin',      7,  'Tablet',    '75mg',     'USV',                2.50, 1200,  120, '2026-01-31', 'Room temperature',   TRUE,  '30049099'),
(19, 'Atorvastatin 40',     'Atorvastatin Calcium',      'Lipitor',       7,  'Tablet',    '40mg',     'Pfizer',            22.00,  600,  70,  '2025-12-31', 'Room temperature',   TRUE,  '30049099'),
(20, 'Clopidogrel 75',      'Clopidogrel Bisulfate',     'Plavix',        7,  'Tablet',    '75mg',     'Sanofi',            28.00,  480,  60,  '2025-11-30', 'Room temperature',   TRUE,  '30049099'),
(21, 'Warfarin 5',          'Warfarin Sodium',           'Warf',          10, 'Tablet',    '5mg',      'Cipla',             15.00,   18,  20,  '2024-04-23', 'Room temperature',   TRUE,  '30049099'),
(22, 'Enoxaparin 60',       'Enoxaparin Sodium',         'Clexane',       10, 'Injection', '60mg/0.6ml','Sanofi',          180.00,  120,  20,  '2025-06-30', 'Refrigerate 2-8°C',  TRUE,  '30042090'),
(23, 'Salbutamol Inhaler',  'Salbutamol',                'Asthalin',      11, 'Inhaler',   '100mcg/dose','Cipla',            85.00,  200,  30,  '2025-08-31', 'Room temperature',   TRUE,  '30059099'),
(24, 'Budesonide Inhaler',  'Budesonide+Formoterol',     'Foracort',      11, 'Inhaler',   '200/6mcg', 'Cipla',             280.00,  150,  25,  '2025-07-31', 'Room temperature',   TRUE,  '30059099'),
(25, 'Prednisolone 10',     'Prednisolone',              'Wysolone',      13, 'Tablet',    '10mg',     'Pfizer',            12.00,  300,  40,  '2025-09-30', 'Room temperature',   TRUE,  '30049099'),
(26, 'Methylprednisolone',  'Methylprednisolone Sodium', 'Solu-Medrol',   13, 'Injection', '500mg',    'Pfizer',            320.00,   60,  15,  '2025-06-30', 'Room temperature',   TRUE,  '30042090'),
(27, 'Digoxin 0.25',        'Digoxin',                   'Lanoxin',       7,  'Tablet',    '0.25mg',   'Aspen',              8.00,  220,  30,  '2025-12-31', 'Room temperature',   TRUE,  '30049099'),
(28, 'Sertraline 50',       'Sertraline HCl',            'Zoloft',        12, 'Tablet',    '50mg',     'Pfizer',            22.00,  280,  35,  '2025-10-31', 'Room temperature',   TRUE,  '30049099'),
(29, 'Topiramate 50',       'Topiramate',                'Topamax',       14, 'Tablet',    '50mg',     'Janssen',           48.00,  180,  25,  '2025-08-31', 'Room temperature',   TRUE,  '30049099'),
(30, 'Levothyroxine 50',    'Levothyroxine Sodium',      'Thyronorm',     16, 'Tablet',    '50mcg',    'Abbott',            14.00,  400,  50,  '2025-11-30', 'Room temperature',   TRUE,  '30049099'),
(31, 'Alendronate 70',      'Alendronate Sodium',        'Fosamax',       8,  'Tablet',    '70mg',     'MSD',               32.00,  150,  25,  '2025-09-30', 'Room temperature',   TRUE,  '30049099'),
(32, 'Tamsulosin 0.4',      'Tamsulosin HCl',            'Veltam',        3,  'Capsule',   '0.4mg',    'Wockhardt',         18.00,  180,  30,  '2025-12-31', 'Room temperature',   TRUE,  '30049099'),
(33, 'Ondansetron 4',       'Ondansetron HCl',           'Zofran',        9,  'Tablet',    '4mg',      'GSK',               12.00,  400,  50,  '2025-10-31', 'Room temperature',   TRUE,  '30049099'),
(34, 'Calcium + Vit D3',    'Calcium Carbonate + Vit D3','Shelcal',       8,  'Tablet',    '500mg/250IU','Torrent',         14.00,  500,  60,  '2026-03-31', 'Room temperature',   FALSE, '30049099'),
(35, 'Vitamin B Complex',   'B1+B6+B12',                 'Neurobion',     8,  'Tablet',    'Standard', 'Merck',              6.00,  600,  80,  '2026-01-31', 'Room temperature',   FALSE, '30049099'),
(36, 'Ranitidine 150',      'Ranitidine HCl',            'Zinetac',       6,  'Tablet',    '150mg',    'GSK',                6.00,    8,   30,  '2024-05-31', 'Room temperature',   FALSE, '30049099'),
(37, 'ORS Powder',          'Oral Rehydration Salts',    'Electral',      8,  'Powder',    'Standard', 'FDC',               18.00,  350,  50,  '2026-06-30', 'Room temperature',   FALSE, '30049099'),
(38, 'Dexamethasone 4',     'Dexamethasone',             'Decadron',      13, 'Injection', '4mg/mL',   'MSD',               28.00,  100,  20,  '2025-07-31', 'Room temperature',   TRUE,  '30042090'),
(39, 'Methotrexate 2.5',    'Methotrexate',              'Methofar',      18, 'Tablet',    '2.5mg',    'Pfizer',            45.00,   60,  15,  '2025-06-30', 'Room temperature',   TRUE,  '30049099'),
(40, 'Fluconazole 150',     'Fluconazole',               'Diflucan',      15, 'Tablet',    '150mg',    'Pfizer',            32.00,  200,  30,  '2025-11-30', 'Room temperature',   TRUE,  '30049099');

-- ─────────────────────────────────────────────
-- 17. PRESCRIPTIONS
-- ─────────────────────────────────────────────
INSERT INTO Prescription (prescription_id, consultation_id, patient_id, doctor_id, prescribed_at, valid_till, notes) VALUES
(1, 1, 1,  1, '2024-02-05 09:40:00', '2024-05-05', 'Tab to be taken with food. Avoid salt. Monitor BP daily.'),
(2, 2, 3,  3, '2024-02-06 11:00:00', '2024-05-06', 'Physiotherapy sessions 5x/week. Ice pack after exercise.'),
(3, 3, 5,  1, '2024-02-08 10:00:00', '2024-05-08', 'Do NOT miss medications. Monitor INR weekly.'),
(4, 4, 2,  2, '2024-02-10 11:30:00', '2024-05-10', 'Avoid bright lights. Rest in dark room during headache. MRI follow-up.'),
(5, 5, 1,  1, '2024-04-01 09:30:00', '2024-07-01', 'Diet control strict. Exercise 30 min daily. Monitor BP and FBS at home.'),
(6, 7, 2,  2, '2024-04-05 10:30:00', '2024-07-05', 'Verapamil to be taken at night. Avoid alcohol.'),
(7, 8, 1,  1, '2024-04-11 09:35:00', '2024-07-11', 'HbA1c and Lipid profile after 3 months. Continue current medications.');

INSERT INTO  ionItem (item_id, prescription_id, medicine_id, dosage, frequency, duration_days, route, instructions) VALUES
-- Prescription 1: Patient 1, Hypertension + DM
(1,  1, 7,  '1 tablet',   'Once daily (OD)',      30,  'Oral', 'Morning, before breakfast'),
(2,  1, 8,  '1 tablet',   'Once daily (OD)',      30,  'Oral', 'Morning, with food'),
(3,  1, 11, '1 tablet',   'Twice daily (BD)',     30,  'Oral', 'After meals - morning and night'),
(4,  1, 16, '1 tablet',   'Once daily (OD)',      30,  'Oral', '30 minutes before breakfast'),
-- Prescription 2: Patient 3, Osteoarthritis
(5,  2, 6,  '1 tablet',   'Twice daily (BD)',     14,  'Oral', 'After food. Avoid on empty stomach.'),
(6,  2, 34, '1 tablet',   'Once daily (OD)',      90,  'Oral', 'After dinner'),
(7,  2, 35, '1 tablet',   'Once daily (OD)',      30,  'Oral', 'After breakfast'),
-- Prescription 3: Patient 5, Post-CABG AF
(8,  3, 18, '1 tablet',   'Once daily (OD)',      365, 'Oral', 'After breakfast. Never skip.'),
(9,  3, 19, '1 tablet',   'Once daily (OD)',      365, 'Oral', 'Night, after dinner'),
(10, 3, 9,  '1 tablet',   'Once daily (OD)',      365, 'Oral', 'Morning, with food'),
(11, 3, 21, '1 tablet',   'Once daily (OD)',      90,  'Oral', 'Night. Monitor INR every 2 weeks.'),
(12, 3, 27, '1/2 tablet', 'Once daily (OD)',      365, 'Oral', 'Morning. Monitor digoxin levels.'),
-- Prescription 4: Patient 2, Migraine
(13, 4, 29, '1 tablet',   'Twice daily (BD)',     90,  'Oral', 'Morning and night, after food'),
(14, 4, 5,  '1 tablet',   'As needed (SOS)',      30,  'Oral', 'Only during headache attack. Max 2/day.'),
-- Prescription 5: Patient 1, Updated
(15, 5, 7,  '1 tablet',   'Once daily (OD)',      90,  'Oral', 'Morning'),
(16, 5, 8,  '1 tablet',   'Once daily (OD)',      90,  'Oral', 'Morning'),
(17, 5, 11, '1 tablet',   'Twice daily (BD)',     90,  'Oral', 'After meals'),
(18, 5, 12, '1 tablet',   'Once daily (OD)',      90,  'Oral', 'Before dinner'),
(19, 5, 16, '1 tablet',   'Once daily (OD)',      90,  'Oral', 'Before breakfast'),
-- Prescription 6: Patient 2, Updated Migraine
(20, 6, 29, '1 tablet',   'Once at night',        90,  'Oral', 'Reduce dose after 3 months.'),
(21, 6, 4,  '2 tablets',  'As needed (SOS)',      30,  'Oral', 'During headache. Max 4g/day total.'),
-- Prescription 7: Patient 1, Latest
(22, 7, 7,  '1 tablet',   'Once daily (OD)',      90,  'Oral', 'Morning'),
(23, 7, 11, '1 tablet',   'Twice daily (BD)',     90,  'Oral', 'After meals'),
(24, 7, 12, '1 tablet',   'Once daily (OD)',      90,  'Oral', 'Before dinner'),
(25, 7, 19, '1 tablet',   'Once daily (OD)',      90,  'Oral', 'Night');

-- ─────────────────────────────────────────────
-- 18. LAB TECHNICIANS
-- ─────────────────────────────────────────────
INSERT INTO LabTechnician (lab_tech_id, user_id, first_name, last_name, gender, phone, employee_id, qualification, specialization, shift, joining_date) VALUES
(1, 16, 'Rahul',   'Dev',    'Male',   '9844100001', 'EMP-LAB-001', 'B.Sc MLT, DMLT',    'Hematology',   'Morning', '2023-07-15'),
(2, 17, 'Pooja',   'Iyer',   'Female', '9844100002', 'EMP-LAB-002', 'B.Sc MLT, DMLT',    'Biochemistry', 'Morning', '2023-07-15'),
(3, 18, 'Santosh', 'Reddy',  'Male',   '9844100003', 'EMP-LAB-003', 'B.Sc MLT, M.Sc',   'Microbiology', 'Night',   '2023-08-01');

-- ─────────────────────────────────────────────
-- 19. LAB TEST CATEGORIES
-- ─────────────────────────────────────────────
INSERT INTO LabTestCategory (test_cat_id, category_name) VALUES
(1, 'Hematology'),
(2, 'Biochemistry'),
(3, 'Microbiology'),
(4, 'Serology / Immunology'),
(5, 'Urine Analysis'),
(6, 'Radiology / Imaging'),
(7, 'Histopathology'),
(8, 'Endocrinology'),
(9, 'Cardiac Markers'),
(10,'Coagulation');

-- ─────────────────────────────────────────────
-- 20. LAB TESTS
-- ─────────────────────────────────────────────
INSERT INTO LabTest (test_id, test_name, test_code, test_cat_id, description, sample_type, sample_volume, normal_range, unit, turnaround_hours, price, equipment_required) VALUES
(1,  'Complete Blood Count (CBC)',         'CBC',      1, 'Differential WBC, RBC, platelets, Hb, PCV', 'Blood (EDTA)', '3 mL',  'WBC 4000-11000/μL, Hb M:13-17 F:12-15 g/dL', 'g/dL',   4,   250.00, 'Sysmex XN-1000 Hematology Analyzer'),
(2,  'Hemoglobin',                         'HB',       1, 'Hemoglobin quantification',                'Blood (EDTA)', '2 mL',  'Male: 13-17, Female: 12-15',                  'g/dL',   2,    80.00, 'Hematology Analyzer'),
(3,  'Peripheral Blood Smear',             'PBS',      1, 'Manual WBC differential and morphology',     'Blood (EDTA)', '2 mL',  'Normal morphology',                           '-',       8,   150.00, 'Microscope, Staining'),
(4,  'ESR (Westergren)',                   'ESR',      1, 'Erythrocyte sedimentation rate',             'Blood (EDTA)', '2 mL',  'Male: <15, Female: <20 mm/1hr',               'mm/hr',   2,    80.00, 'Westergren tube'),
(5,  'Fasting Blood Glucose',              'FBG',      2, '8-hour fasting plasma glucose',              'Blood (Fluoride)','2 mL','70-100',                                     'mg/dL',  2,    60.00, 'Beckman Coulter AU 480'),
(6,  'Post Prandial Blood Glucose (PPBS)', 'PPBS',     2, '2-hour post meal glucose',                   'Blood (Fluoride)','2 mL','<140',                                       'mg/dL',  2,    60.00, 'Biochemistry Analyzer'),
(7,  'HbA1c (Glycosylated Hb)',            'HBA1C',    2, 'Average blood sugar over 3 months',          'Blood (EDTA)', '2 mL',  'Normal <5.7%, Pre-DM 5.7-6.4%, DM ≥6.5%',     '%',      24,   400.00, 'Bio-Rad D-100 HPLC'),
(8,  'Lipid Profile',                      'LIPID',    2, 'TC, TG, HDL, LDL, VLDL',                    'Blood (Serum)', '4 mL',  'TC <200, LDL <100, HDL >40, TG <150 mg/dL',   'mg/dL',  12,   500.00, 'Biochemistry Analyzer'),
(9,  'Liver Function Test (LFT)',          'LFT',      2, 'Bilirubin, SGPT, SGOT, ALP, Albumin',       'Blood (Serum)', '4 mL',  'SGPT 7-56 IU/L, SGOT 10-40 IU/L',             'IU/L',   8,   600.00, 'Beckman Coulter AU 480'),
(10, 'Kidney Function Test (KFT)',         'KFT',      2, 'BUN, Creatinine, Uric Acid, Electrolytes',  'Blood (Serum)', '4 mL',  'Creatinine M:0.7-1.2, F:0.5-1.0 mg/dL',       'mg/dL',  8,   550.00, 'Biochemistry Analyzer'),
(11, 'Serum Electrolytes',                 'ELEC',     2, 'Na, K, Cl, HCO3',                           'Blood (Serum)', '3 mL',  'Na 135-145, K 3.5-5.0 mEq/L',                 'mEq/L',  4,   300.00, 'Ion Selective Electrode Analyzer'),
(12, 'Uric Acid',                          'UA',       2, 'Serum uric acid',                            'Blood (Serum)', '2 mL',  'Male: 3.5-7.2, Female: 2.6-6.0 mg/dL',        'mg/dL',  4,   120.00, 'Biochemistry Analyzer'),
(13, 'Thyroid Profile (T3, T4, TSH)',      'TFT',      8, 'Free T3, Free T4, TSH',                     'Blood (Serum)', '4 mL',  'TSH 0.5-5.0 mIU/L, FT4 0.9-1.7 ng/dL',        'mIU/L',  24,  700.00, 'CLIA Analyzer'),
(14, 'Troponin-I (cTnI)',                  'TROP',     9, 'Cardiac troponin for MI diagnosis',          'Blood (Serum)', '3 mL',  '<0.04 ng/mL',                                'ng/mL',  2,   800.00, 'Beckman DxI 800'),
(15, 'CK-MB',                              'CKMB',     9, 'Creatine kinase MB isoenzyme',               'Blood (Serum)', '3 mL',  'Male <25, Female <16 U/L',                   'U/L',    4,   500.00, 'Biochemistry Analyzer'),
(16, 'BNP / NT-proBNP',                    'BNP',      9, 'Brain natriuretic peptide (heart failure)',  'Blood (Serum)', '3 mL',  '<100 pg/mL (BNP)',                            'pg/mL',  6,  1200.00, 'Immunoassay Analyzer'),
(17, 'PT / INR',                           'INR',      10,'Prothrombin time, clotting function',        'Blood (Citrate)','3 mL', 'PT: 11-13 sec, INR: 0.8-1.2 (therapeutic: 2-3)','sec',  2,   250.00, 'Stago STA-R Max'),
(18, 'APTT',                               'APTT',     10,'Activated partial thromboplastin time',      'Blood (Citrate)','3 mL', '25-35 seconds',                               'sec',    2,   200.00, 'Coagulation Analyzer'),
(19, 'Blood Culture & Sensitivity',        'BC&S',     3, 'Aerobic and anaerobic culture',              'Blood (Aerobic)','10 mL','No growth',                                   '-',      72,  800.00, 'BacT/ALERT 3D System'),
(20, 'Urine Routine & Microscopy',         'UR&M',     5, 'Physical, chemical, microscopic exam',       'Urine (Midstream)','10 mL','No RBCs/WBCs, No bacteria',                 '-',      4,   100.00, 'Urinalysis Analyzer'),
(21, 'Urine Culture & Sensitivity',        'UC&S',     3, 'Bacterial culture from urine',               'Urine (Midstream)','10 mL','No growth (<1000 cfu/mL)',                  'cfu/mL', 48,  500.00, 'Culture incubator'),
(22, 'Dengue NS1 Antigen',                 'DENGUE',   4, 'Early dengue detection',                     'Blood (Serum)', '3 mL',  'Negative',                                    '-',      6,   600.00, 'ELISA Reader'),
(23, 'Malaria Antigen (PfHRP2/pLDH)',      'MALARIA',  4, 'Rapid malaria detection',                    'Blood (EDTA)', '2 mL',  'Negative',                                    '-',      2,   300.00, 'Rapid Test Kit'),
(24, 'COVID-19 RT-PCR',                    'COVID',    3, 'SARS-CoV-2 RNA detection',                   'Nasopharyngeal Swab','-','Not Detected',                                '-',      24, 1000.00, 'RT-PCR Machine'),
(25, 'Chest X-Ray (PA View)',              'CXR',      6, 'Posterior-anterior chest radiograph',        'N/A',           '-',     'Normal lung fields, heart size, mediastinum', '-',      2,   350.00, 'Digital X-Ray System'),
(26, 'ECG (12-Lead)',                      'ECG',      6, '12-lead electrocardiogram',                  'N/A',           '-',     'Normal sinus rhythm',                         '-',      1,   200.00, 'GE MAC 5500 ECG Machine'),
(27, '2D Echocardiography',                'ECHO',     6, 'Cardiac structure and function',              'N/A',           '-',     'EF >55%, Normal wall motion',                 '%',      4,  2500.00, 'Philips IE33 Echo Machine'),
(28, 'USG Abdomen & Pelvis',               'USG-AP',   6, 'Abdominal and pelvic ultrasound',             'N/A',           '-',     'Normal organ size and echogenicity',          '-',      4,  1200.00, 'GE LOGIQ P9 Ultrasound'),
(29, 'MRI Brain (Plain & Contrast)',       'MRI-B',    6, 'Magnetic resonance imaging of brain',        'N/A',           '-',     'No focal lesions, normal white matter',       '-',     12,  6500.00, 'Siemens Skyra 3T MRI'),
(30, 'Serum Ferritin',                     'FERR',     2, 'Iron storage marker',                        'Blood (Serum)', '2 mL',  'Male: 30-400, Female: 15-150 ng/mL',          'ng/mL',  8,   350.00, 'Immunoassay Analyzer'),
(31, 'Vitamin B12',                        'B12',      8, 'Cobalamin level',                            'Blood (Serum)', '2 mL',  '200-900 pg/mL',                               'pg/mL',  24,  600.00, 'CLIA Analyzer'),
(32, 'Vitamin D (25-OH)',                  'VITD',     8, '25-hydroxyvitamin D',                        'Blood (Serum)', '3 mL',  'Deficient <20, Insufficient 20-29, Normal ≥30 ng/mL','ng/mL',24, 800.00, 'CLIA Analyzer'),
(33, 'HCV Antibody',                       'HCV',      4, 'Hepatitis C virus antibody',                 'Blood (Serum)', '3 mL',  'Non-reactive',                                '-',      6,   500.00, 'ELISA Reader'),
(34, 'HBsAg',                              'HBSAG',    4, 'Hepatitis B surface antigen',                'Blood (Serum)', '3 mL',  'Non-reactive',                                '-',      4,   300.00, 'ELISA Reader'),
(35, 'HIV 1&2 Antibody',                   'HIV',      4, 'HIV rapid antibody test',                    'Blood (Serum)', '2 mL',  'Non-reactive',                                '-',      4,   400.00, 'Rapid Test / ELISA');

-- ─────────────────────────────────────────────
-- 21. LAB ORDERS
-- ─────────────────────────────────────────────
INSERT INTO LabOrder (order_id, patient_id, doctor_id, consultation_id, ordered_at, priority, status, notes) VALUES
(1,  1,  1,  1, '2024-02-05 09:45:00', 'Routine', 'Completed', 'Pre-treatment baseline. FBS, Lipid profile, ECG, ECHO.'),
(2,  3,  3,  2, '2024-02-06 11:05:00', 'Routine', 'Completed', 'Knee X-ray bilateral. Uric acid to rule out gout.'),
(3,  5,  1,  3, '2024-02-08 10:05:00', 'Urgent',  'Completed', 'INR monitoring. Post-CABG BNP level.'),
(4,  2,  2,  4, '2024-02-10 11:35:00', 'Routine', 'Completed', 'MRI Brain. CBC and ESR.'),
(5,  5,  1,  6, '2024-04-03 10:00:00', 'STAT',    'Completed', 'NSTEMI workup. Troponin serial x3, CK-MB, ECG, ECHO, CBC, KFT, Electrolytes.'),
(6,  1,  1,  5, '2024-04-01 09:35:00', 'Routine', 'Completed', 'HbA1c, Lipid profile, KFT.'),
(7,  1,  1,  7, '2024-04-11 09:40:00', 'Routine', 'Ordered',   'HbA1c 3-monthly review. Lipid profile. Urine routine.'),
(8,  2,  2,  NULL,'2024-04-11 09:50:00','Routine', 'Sample Collected', 'CBC and ESR for headache workup.'),
(9,  8,  1,  NULL,'2024-04-07 09:10:00','STAT',    'Completed', 'INR monitoring for warfarin. ECG.'),
(10, 7,  6,  NULL,'2024-03-01 12:00:00','Urgent',  'Completed', 'CBC, Peripheral smear, LFT, Coagulation profile - leukemia monitoring.'),
(11, 4,  4,  NULL,'2024-04-11 10:40:00','Routine', 'Ordered',   'Thyroid profile, CBC, USG pelvis.'),
(12, 6,  5,  NULL,'2024-04-11 11:05:00','Routine', 'Ordered',   'TSH level monitoring.'),
(13, 9,  5,  NULL,'2024-04-11 11:40:00','Routine', 'Ordered',   'Urea breath test / H. pylori stool antigen. LFT.'),
(14, 11,  5,  NULL,'2024-04-11 12:05:00','Routine', 'Ordered',   'PFT, CBC, Serum IgE.'),
(15, 13, 5,  NULL,'2024-04-11 14:10:00','Routine', 'Ordered',   'PSA, KFT, Urine routine.');

INSERT INTO LabOrderItem (order_item_id, order_id, test_id) VALUES
-- Order 1: Baseline for Patient 1
(1,  1, 5),  (2,  1, 7),  (3,  1, 8),  (4,  1, 10), (5,  1, 26), (6,  1, 27),
-- Order 2: Patient 3, knee
(7,  2, 12), (8,  2, 25),
-- Order 3: Patient 5, post-CABG
(9,  3, 17), (10, 3, 16),
-- Order 4: Patient 2, headache
(11, 4, 29), (12, 4, 1),  (13, 4, 4),
-- Order 5: Patient 5, NSTEMI STAT
(14, 5, 14), (15, 5, 15), (16, 5, 26), (17, 5, 27), (18, 5, 1),  (19, 5, 10), (20, 5, 11),
-- Order 6: Patient 1, HbA1c
(21, 6, 7),  (22, 6, 8),  (23, 6, 10),
-- Order 7: Patient 1 today
(24, 7, 7),  (25, 7, 8),  (26, 7, 20),
-- Order 8: Patient 2 today
(27, 8, 1),  (28, 8, 4),
-- Order 9: Patient 8, INR
(29, 9, 17), (30, 9, 26),
-- Order 10: Patient 7, leukemia
(31, 10, 1), (32, 10, 3), (33, 10, 9), (34, 10, 17),(35, 10, 18);

-- ─────────────────────────────────────────────
-- 22. LAB RESULTS
-- ─────────────────────────────────────────────
INSERT INTO LabResult (result_id, order_item_id, lab_tech_id, sample_collected_at, result_value, unit, normal_range, status, remarks, verified_by, reported_at) VALUES
-- Order 1 results (Patient 1 baseline)
(1,  1,  2, '2024-02-05 10:00:00', '204',            'mg/dL',   '70-100',           'Abnormal',  'Elevated fasting glucose. Consistent with Type 2 DM.',            2, '2024-02-05 12:00:00'),
(2,  2,  2, '2024-02-05 10:00:00', '8.2',            '%',       '<5.7',             'Abnormal',  'Poor glycemic control. Target <7.0%. Medication intensification needed.', 2, '2024-02-05 23:00:00'),
(3,  3,  2, '2024-02-05 10:00:00', 'TC:228 LDL:148 HDL:38 TG:210 VLDL:42', 'mg/dL', 'TC<200, LDL<100, HDL>40, TG<150', 'Abnormal', 'Mixed dyslipidemia. LDL elevated, HDL low.', 2, '2024-02-05 22:00:00'),
(4,  4,  2, '2024-02-05 10:00:00', 'Creatinine:1.1 BUN:18 Uric Acid:6.8', 'mg/dL', 'Cr:0.7-1.2', 'Normal', 'Kidney function within normal limits.', 2, '2024-02-05 18:00:00'),
(5,  5,  1, '2024-02-05 10:15:00', 'NSR. LVH changes. ST changes V5-V6.', '-',    'Normal sinus rhythm', 'Abnormal', 'Left ventricular hypertrophy. Lateral ST segment changes. Cardiologist review advised.', 1, '2024-02-05 10:45:00'),
-- Order 3 results (Patient 5, post-CABG)
(6,  9,  1, '2024-02-08 10:15:00', '2.8',            'sec-INR', '2-3 (therapeutic)', 'Normal',   'INR within therapeutic range for AF. Continue Warfarin.',         3, '2024-02-08 12:15:00'),
(7,  10, 2, '2024-02-08 10:15:00', '385',            'pg/mL',   '<100',             'Critical',  'Markedly elevated BNP. Significant cardiac stress. Clinical correlation essential.', 2, '2024-02-08 16:15:00'),
-- Order 4 results (Patient 2, headache)
(8,  11, 3, '2024-02-10 12:00:00', 'No focal lesion. No aneurysm. No bleed. Bilateral maxillary sinusitis noted.', '-', 'Normal', 'Normal', 'MRI Brain: Normal brain parenchyma. Incidental finding of maxillary sinusitis.', 1, '2024-02-10 21:00:00'),
(9,  12, 1, '2024-02-10 12:00:00', 'WBC:7200 Hb:12.8 Platelets:2.1L HCT:38%', '-', 'WBC 4-11K', 'Normal', 'CBC within normal limits.', 1, '2024-02-10 16:00:00'),
-- Order 5 results (Patient 5, NSTEMI STAT)
(10, 14, 1, '2024-04-03 10:15:00', '2.8',           'ng/mL',   '<0.04',            'Critical',  'Troponin-I significantly elevated. NSTEMI confirmed. Immediate cardiology intervention.', 2, '2024-04-03 12:15:00'),
(11, 15, 2, '2024-04-03 10:15:00', '88',            'U/L',     'M<25',             'Abnormal',  'CK-MB elevated. Consistent with myocardial damage.', 2, '2024-04-03 14:15:00'),
(12, 16, 1, '2024-04-03 10:20:00', 'ST depression V1-V4. T inversion V5-V6.', '-', 'NSR', 'Abnormal', 'NSTEMI pattern. Urgent cardiology consult.', 1, '2024-04-03 10:50:00'),
-- Order 6 results (Patient 1, HbA1c follow-up)
(13, 21, 2, '2024-04-01 10:00:00', '7.8',            '%',       '<5.7',             'Abnormal',  'HbA1c above target. Medication escalation warranted.', 2, '2024-04-01 22:00:00'),
(14, 22, 2, '2024-04-01 10:00:00', 'TC:210 LDL:138 HDL:40 TG:185', 'mg/dL', 'TC<200', 'Abnormal', 'Borderline high cholesterol. On statin - dose may need increase.', 2, '2024-04-01 22:00:00'),
(15, 23, 2, '2024-04-01 10:00:00', 'Creatinine:1.0 BUN:16', 'mg/dL', 'Cr:0.7-1.2', 'Normal', 'Stable kidney function.', 2, '2024-04-01 18:00:00'),
-- Order 9 (Patient 8, INR monitoring)
(16, 29, 1, '2024-04-07 09:20:00', '2.4',            'INR',     '2-3 (therapeutic)', 'Normal',   'INR in therapeutic range. Continue Warfarin 5mg OD.', 3, '2024-04-07 11:20:00'),
-- Order 10 (Patient 7, leukemia CBC)
(17, 31, 1, '2024-03-01 12:15:00', 'WBC:82000 Hb:7.2 Plt:42000 Blast cells:68%', '-', 'WBC 4-11K', 'Critical', 'Severe leukocytosis with blast cells. Thrombocytopenia. Anemia. Consistent with ALL blast crisis.', 3, '2024-03-01 16:15:00'),
(18, 32, 1, '2024-03-01 12:15:00', 'Blast cells 68%. Auer rods absent. Lymphoblast morphology.', '-', 'Normal morphology', 'Critical', 'Peripheral smear: Lymphoblasts predominant. ALL confirmed morphologically.', 3, '2024-03-01 18:00:00');

-- ─────────────────────────────────────────────
-- 23. PHARMACISTS
-- ─────────────────────────────────────────────
INSERT INTO Pharmacist (pharmacist_id, user_id, first_name, last_name, license_number, phone, shift) VALUES
(1, 19, 'Meera',  'Joshi', 'PCI-PHM-001234', '9833100001', 'Morning'),
(2, 20, 'Deepak', 'Shah',  'PCI-PHM-005678', '9833100002', 'Evening');

-- ─────────────────────────────────────────────
-- 24. PHARMACY DISPENSE
-- ─────────────────────────────────────────────
INSERT INTO PharmacyDispense (dispense_id, prescription_id, patient_id, pharmacist_id, dispensed_at, total_amount, payment_status) VALUES
(1, 1, 1,  1, '2024-02-05 11:00:00', 604.00,  'Paid'),
(2, 2, 3,  1, '2024-02-06 12:00:00', 622.00,  'Paid'),
(3, 3, 5,  2, '2024-02-08 11:00:00', 1520.00, 'Paid'),
(4, 4, 2,  1, '2024-02-10 12:30:00', 1710.00, 'Paid'),
(5, 5, 1,  1, '2024-04-01 10:30:00', 1260.00, 'Paid'),
(6, 7, 1,  1, '2024-04-11 10:00:00', 1152.00, 'Pending');

INSERT INTO DispenseItem (dispense_item_id, dispense_id, medicine_id, quantity, unit_price, total_price) VALUES
-- Dispense 1: Prescription 1 (Patient 1)
(1,  1, 7,  30, 5.00,  150.00),
(2,  1, 8,  30, 12.00, 360.00),
(3,  1, 11, 60, 4.50,  270.00),
(4,  1, 16, 30, 8.00,  240.00),
-- Dispense 2: Prescription 2 (Patient 3)
(5,  2, 6,  28, 8.50,  238.00),
(6,  2, 34, 90, 14.00, 1260.00),
(7,  2, 35, 30, 6.00,  180.00),
-- Dispense 3: Prescription 3 (Patient 5, post-CABG)
(8,  3, 18, 30, 2.50,  75.00),
(9,  3, 19, 30, 22.00, 660.00),
(10, 3, 9,  30, 6.50,  195.00),
(11, 3, 21, 30, 15.00, 450.00),
(12, 3, 27, 30, 8.00,  240.00),
-- Dispense 4: Prescription 4 (Patient 2, migraine)
(13, 4, 29, 60, 48.00, 2880.00),
(14, 4, 5,  15, 7.00,  105.00),
-- Dispense 5: Prescription 5 (Patient 1, updated)
(15, 5, 7,  90, 5.00,  450.00),
(16, 5, 8,  90, 12.00, 1080.00),
(17, 5, 11, 180, 4.50, 810.00),
(18, 5, 12, 90, 14.00, 1260.00),
(19, 5, 16, 90, 8.00,  720.00),
-- Dispense 6: Latest (Patient 1)
(20, 6, 7,  90, 5.00,  450.00),
(21, 6, 11, 180,4.50,  810.00),
(22, 6, 12, 90, 14.00, 1260.00),
(23, 6, 19, 90, 22.00, 1980.00);

-- ─────────────────────────────────────────────
-- 25. INVOICES
-- ─────────────────────────────────────────────
INSERT INTO Invoice (invoice_id, invoice_number, patient_id, admission_id, generated_by, invoice_date, subtotal, discount, tax, total_amount, paid_amount, due_amount, payment_status, payment_mode, notes) VALUES
(1, 'APL-INV-240001', 1,  NULL, 1, '2024-02-05 11:30:00', 1700.00,  0.00,   0.00,  1700.00,  1700.00, 0.00,    'Paid',    'UPI',       'OPD visit + Lab + Medicines'),
(2, 'APL-INV-240002', 3,  NULL, 2, '2024-02-06 12:30:00', 1500.00,  0.00,   0.00,  1500.00,  1500.00, 0.00,    'Paid',    'Cash',      'OPD visit + X-ray + Medicines'),
(3, 'APL-INV-240003', 5,  NULL, 1, '2024-02-08 11:30:00', 3420.00, 200.00,  0.00,  3220.00,  3220.00, 0.00,    'Paid',    'Card',      'Follow-up + Lab + Medicines. Senior citizen discount applied.'),
(4, 'APL-INV-240004', 2,  NULL, 2, '2024-02-10 13:00:00', 8200.00,  0.00, 820.00, 9020.00,  5000.00, 4020.00, 'Partial', 'Insurance', 'OPD + MRI Brain + Medicines. Insurance claim pending.'),
(5, 'APL-INV-240005', 5,  1,    1, '2024-04-10 10:00:00',45800.00,  0.00,   0.00, 45800.00, 20000.00,25800.00,'Partial', 'Insurance', 'IPD: CCU charges 7 days + procedures + medicines + lab. Insurance pre-auth applied.'),
(6, 'APL-INV-240006', 2,  4,    2, '2024-03-20 12:00:00', 9500.00,  0.00, 950.00,10450.00, 10450.00, 0.00,    'Paid',    'Card',      'IPD 5 days: Room + Lab + Medicines. Fully paid.'),
(7, 'APL-INV-240007', 1,  NULL, 1, '2024-04-01 10:00:00', 2200.00,  0.00,   0.00,  2200.00,  2200.00, 0.00,    'Paid',    'UPI',       'Follow-up OPD + Lab + Medicines'),
(8, 'APL-INV-240008', 8,  3,    3, '2024-04-07 10:00:00',12000.00,  0.00,   0.00, 12000.00, 12000.00, 0.00,    'Paid',    'Card',      'IPD: AF management. Room 2 days. Procedures.'),
(9, 'APL-INV-240009', 1,  NULL, 1, '2024-04-11 10:30:00', 1800.00,  0.00,   0.00,  1800.00,     0.00, 1800.00, 'Unpaid',  NULL,        'Today OPD + Lab ordered. Bill pending collection.');

INSERT INTO InvoiceItem (item_id, invoice_id, item_type, description, quantity, unit_price, total_price) VALUES
-- Invoice 1
(1,  1, 'Consultation', 'OPD Consultation - Dr. Ankit Mehta (Cardiology)',     1, 800.00,  800.00),
(2,  1, 'Lab Test',     'Fasting Blood Glucose (FBG)',                         1, 60.00,   60.00),
(3,  1, 'Lab Test',     'HbA1c',                                               1, 400.00,  400.00),
(4,  1, 'Lab Test',     'Lipid Profile',                                       1, 500.00,  500.00),
(5,  1, 'Lab Test',     'ECG 12-Lead',                                         1, 200.00,  200.00),
-- Invoice 2
(6,  2, 'Consultation', 'OPD Consultation - Dr. Raj Singh (Orthopedics)',      1, 700.00,  700.00),
(7,  2, 'Lab Test',     'Chest X-Ray (Knee AP/Lateral)',                       1, 350.00,  350.00),
(8,  2, 'Lab Test',     'Uric Acid',                                           1, 120.00,  120.00),
(9,  2, 'Medicine',     'Medicines dispensed',                                 1, 622.00,  622.00),
-- Invoice 4 (Partial - insurance)
(10, 4, 'Consultation', 'OPD Consultation - Dr. Sana Khan (Neurology)',        1, 1000.00, 1000.00),
(11, 4, 'Lab Test',     'MRI Brain (Plain + Contrast)',                        1, 6500.00, 6500.00),
(12, 4, 'Lab Test',     'CBC',                                                 1, 250.00,  250.00),
(13, 4, 'Lab Test',     'ESR',                                                 1, 80.00,   80.00),
(14, 4, 'Medicine',     'Topiramate 50mg x60 + Combiflam x15',                 1, 2880.00, 2880.00),
-- Invoice 5 (IPD - CCU)
(15, 5, 'Room',         'CCU Room charges (7 days x ₹8000/day)',               7, 8000.00, 56000.00),
(16, 5, 'Procedure',    'Coronary angiography',                                1, 15000.00,15000.00),
(17, 5, 'Lab Test',     'Troponin-I (x3 serial)',                              3, 800.00,  2400.00),
(18, 5, 'Lab Test',     'ECHO 2D',                                             1, 2500.00, 2500.00),
(19, 5, 'Medicine',     'Enoxaparin 60mg x14 doses + other medicines',         1, 4200.00, 4200.00),
-- Invoice 7
(20, 7, 'Consultation', 'Follow-up - Dr. Ankit Mehta',                         1, 400.00,  400.00),
(21, 7, 'Lab Test',     'HbA1c',                                               1, 400.00,  400.00),
(22, 7, 'Lab Test',     'Lipid Profile',                                       1, 500.00,  500.00),
(23, 7, 'Medicine',     'Medicines dispensed (3-month supply)',                1, 1260.00, 1260.00),
-- Invoice 9 (today, unpaid)
(24, 9, 'Consultation', 'OPD Follow-up - Dr. Ankit Mehta',                     1, 400.00,  400.00),
(25, 9, 'Lab Test',     'HbA1c (ordered)',                                     1, 400.00,  400.00),
(26, 9, 'Lab Test',     'Lipid Profile (ordered)',                             1, 500.00,  500.00),
(27, 9, 'Lab Test',     'Urine Routine & Microscopy (ordered)',                1, 100.00,  100.00);

-- ─────────────────────────────────────────────
-- 26. STAFF SCHEDULE
-- ─────────────────────────────────────────────
INSERT INTO StaffSchedule (schedule_id, user_id, role_id, work_date, shift_start, shift_end, status) VALUES
-- Doctors - week schedule
(1,  6,  3, '2024-04-11', '08:00:00', '16:00:00', 'Present'),
(2,  7,  3, '2024-04-11', '14:00:00', '22:00:00', 'Present'),
(3,  8,  3, '2024-04-11', '08:00:00', '16:00:00', 'Present'),
(4,  9,  3, '2024-04-11', '08:00:00', '16:00:00', 'Absent'),
(5,  10, 3, '2024-04-11', '08:00:00', '16:00:00', 'Present'),
(6,  11, 3, '2024-04-11', '08:00:00', '16:00:00', 'Present'),
-- Receptionists
(7,  3,  2, '2024-04-11', '07:00:00', '15:00:00', 'Present'),
(8,  4,  2, '2024-04-11', '15:00:00', '23:00:00', 'Scheduled'),
(9,  5,  2, '2024-04-11', '07:00:00', '15:00:00', 'Present'),
-- Lab techs
(10, 16, 5, '2024-04-11', '07:00:00', '15:00:00', 'Present'),
(11, 17, 5, '2024-04-11', '07:00:00', '15:00:00', 'Present'),
(12, 18, 5, '2024-04-11', '22:00:00', '06:00:00', 'Scheduled'),
-- Pharmacists
(13, 19, 6, '2024-04-11', '08:00:00', '16:00:00', 'Present'),
(14, 20, 6, '2024-04-11', '16:00:00', '24:00:00', 'Scheduled'),
-- Next day
(15, 6,  3, '2024-04-12', '08:00:00', '16:00:00', 'Scheduled'),
(16, 7,  3, '2024-04-12', '14:00:00', '22:00:00', 'Scheduled'),
(17, 9,  3, '2024-04-12', '08:00:00', '16:00:00', 'Scheduled'),
(18, 3,  2, '2024-04-12', '07:00:00', '15:00:00', 'Scheduled'),
(19, 16, 5, '2024-04-12', '07:00:00', '15:00:00', 'Scheduled'),
(20, 19, 6, '2024-04-12', '08:00:00', '16:00:00', 'Scheduled');

-- ─────────────────────────────────────────────
-- 27. AUDIT LOG
-- ─────────────────────────────────────────────
INSERT INTO AuditLog (log_id, user_id, action, table_name, record_id, old_values, new_values, ip_address, logged_at) VALUES
(1,  1,  'INSERT', 'Patient',     1,    NULL,                                        '{"reg_no":"APL-2024-0001","name":"Ravi Sharma"}',       '192.168.1.10', '2024-01-15 09:31:00'),
(2,  1,  'INSERT', 'Patient',     2,    NULL,                                        '{"reg_no":"APL-2024-0002","name":"Priya Verma"}',        '192.168.1.10', '2024-02-01 10:16:00'),
(3,  6,  'INSERT', 'Appointment', 1,    NULL,                                        '{"patient_id":1,"doctor_id":1,"date":"2024-02-05"}',     '192.168.1.12', '2024-02-05 08:45:00'),
(4,  6,  'UPDATE', 'Appointment', 1,    '{"status":"Scheduled"}',                    '{"status":"Completed"}',                                 '192.168.1.12', '2024-02-05 10:30:00'),
(5,  19, 'INSERT', 'PharmacyDispense', 1, NULL,                                      '{"patient_id":1,"total_amount":604}',                    '192.168.1.20', '2024-02-05 11:01:00'),
(6,  1,  'UPDATE', 'Medicine',    21,   '{"stock_quantity":200}',                    '{"stock_quantity":18}',                                  '192.168.1.10', '2024-02-08 11:15:00'),
(7,  3,  'LOGIN',  'Users',       3,    NULL,                                        '{"login_time":"2024-04-11 07:30:00","ip":"192.168.1.11"}','192.168.1.11','2024-04-11 07:30:00'),
(8,  6,  'LOGIN',  'Users',       6,    NULL,                                        '{"login_time":"2024-04-11 08:30:00","ip":"192.168.1.12"}','192.168.1.12','2024-04-11 08:30:00'),
(9,  1,  'INSERT', 'Admission',   1,    NULL,                                        '{"patient_id":5,"bed_id":1,"reason":"NSTEMI"}',          '192.168.1.10', '2024-04-03 14:31:00'),
(10, 16, 'INSERT', 'LabResult',   10,   NULL,                                        '{"order_item_id":14,"result":"2.8 ng/mL","status":"Critical"}','192.168.1.16','2024-04-03 12:16:00'),
(11, 1,  'UPDATE', 'Bed',         1,    '{"status":"Available"}',                    '{"status":"Occupied"}',                                  '192.168.1.10', '2024-04-03 14:32:00'),
(12, 19, 'UPDATE', 'Medicine',    1,    '{"stock_quantity":501}',                    '{"stock_quantity":480}',                                 '192.168.1.20', '2024-04-05 11:30:00'),
(13, 1,  'INSERT', 'Invoice',     9,    NULL,                                        '{"invoice_no":"APL-INV-240009","total":1800}',           '192.168.1.10', '2024-04-11 10:31:00'),
(14, 2,  'UPDATE', 'Patient',     5,    '{"status":"Active"}',                       '{"status":"Admitted"}',                                  '192.168.1.10', '2024-04-03 14:35:00'),
(15, 1,  'DELETE', 'StaffSchedule',4,   '{"user_id":9,"date":"2024-04-10","status":"Scheduled"}', NULL,                                        '192.168.1.10', '2024-04-10 18:00:00');

-- ─────────────────────────────────────────────
-- RE-ENABLE FK CHECKS
-- ─────────────────────────────────────────────
SET FOREIGN_KEY_CHECKS = 1;