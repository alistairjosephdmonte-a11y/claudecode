#!/usr/bin/env python3
"""Generate a ready-to-use Pipeline Tracker Excel workbook.

Creates output/Pipeline_Tracker.xlsx with:
- Pipeline sheet: all data with validation, conditional formatting, auto-filter
- Dashboard sheet: live COUNTIF/SUMIF formulas
- Closed Deals / Active Pipeline / Lost Deals sheets
"""

import os
import re
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, numbers
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule, FormulaRule

# ── Configuration ──

HEADERS = [
    "Date", "Brand Name", "Type of Scope", "Handled by", "POC Name",
    "Phone", "Email", "Stage", "Costs", "Proposal Date/Follow up", "Status"
]

STAGES = ["First Call", "Pitch", "Commercials", "Closed", "Didnt work out"]
ACTIVE_STAGES = ["First Call", "Pitch", "Commercials"]
HANDLERS = ["Tan", "Ally"]
SCOPES = ["Branding", "Web", "SMM", "Campaign", "Creatives", "Coffee table Book"]

# ── Styles ──

HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
HEADER_FILL = PatternFill(start_color="1A237E", end_color="1A237E", fill_type="solid")
SECTION_FILL = PatternFill(start_color="E8EAF6", end_color="E8EAF6", fill_type="solid")
SUBHEADER_FILL = PatternFill(start_color="CFD8DC", end_color="CFD8DC", fill_type="solid")
ALT_ROW_FILL = PatternFill(start_color="F5F5F5", end_color="F5F5F5", fill_type="solid")
GREEN_FILL = PatternFill(start_color="C8E6C9", end_color="C8E6C9", fill_type="solid")
RED_FILL = PatternFill(start_color="FFCDD2", end_color="FFCDD2", fill_type="solid")
YELLOW_FILL = PatternFill(start_color="FFF9C4", end_color="FFF9C4", fill_type="solid")
ORANGE_FILL = PatternFill(start_color="FFE0B2", end_color="FFE0B2", fill_type="solid")
TITLE_FONT = Font(bold=True, color="FFFFFF", size=18)
SECTION_FONT = Font(bold=True, size=13)
BOLD_FONT = Font(bold=True)
CURRENCY_FMT = '₹#,##,##0'
PCT_FMT = '0.0%'
THIN_BORDER = Border(
    bottom=Side(style="thin", color="E0E0E0")
)


# ── Data ──

RAW_DATA = [
    ["", "Food Brand Launch", "Branding", "Tan", "Akshay", "9833814029", "", "Didnt work out", "-", "", "Didnt work out because of costs."],
    ["", "The Premium Basket", "Branding", "Ally", "Ebrahim Kothari", "8828192685", "ebrahim@thepremiumbasket.com", "Didnt work out", "₹1,675,000.00", "", "We've shared the signed NDA with the client"],
    ["", "Miss Claire", "Branding", "Ally", "Mallika Ahar", "Not available", "", "Didnt work out", "₹1,225,000.00", "", "SPOC has been unresponsive."],
    ["", "Raindus Beauty Care", "Branding", "Ally", "Saumya", "7801904359", "admin@eurekacosmo.com", "Didnt work out", "₹1,225,000.00", "", "Branding proposal shared."],
    ["", "Multichem", "Branding", "Ally", "Sejal Jadiyar", "7738247802", "hello@multichemindia.com", "Didnt work out", "₹745,000.00", "", "Awaiting an update from the founder."],
    ["", "Restaurant", "Branding", "Ally", "Ashwin", "73027 39698", "ashwin2002singh@gmail.com", "Closed", "₹1,200,000.00", "", "Closed. Awaiting advance payment, client has mentioned that is in process."],
    ["", "Bongchie", "Branding", "Ally", "Tushar", "9454748677", "tushar@bongchie.com", "Didnt work out", "₹1,400,000.00", "", "Follow up done on the 1st July. No response. Awaiting a response."],
    ["", "Sweet Dreams", "Branding", "Ally", "Khushi", "98709 10111", "khushi.apwig@gmail.com", "Closed", "₹1,000,000.00", "", "Contract needs to be shared"],
    ["", "KSM Ashwagandha", "Branding, Web", "Tan", "Kartikeya", "98490 30798", "kartikeya@ixoreal.com", "Closed", "₹325,000.00", "", "Project completed."],
    ["", "Welspun", "Branding", "Ally", "Alok", "9998003155", "Alok_Bhinde@welspun.com", "Didnt work out", "", "", "Client has said that CMO is travelling and this will take sometime to close on."],
    ["", "Un'layered", "Branding", "Ally", "Bhawna", "9528255005", "bhawnasharmaofficial@gmail.com", "Didnt work out", "₹1,000,000.00", "", "Call to be made on 2nd July 2025."],
    ["", "Nilambari Sarees", "Branding, Web", "Tan", "Pranav", "88004 77886", "pranavnilambari@gmail.com", "Commercials", "₹1,200,000.00", "", "He ghosted us."],
    ["", "Stationery Brand", "Branding", "Ally", "Radhika", "8889444400", "radhika@krishnaunited.com", "Closed", "₹500,000.00", "", "Branding proposal closed."],
    ["", "CtrlS", "Branding", "Ally", "Pragun", "9372910823", "pragun.narang@ctrls.in", "Commercials", "₹3,500,000.00", "", "Client will update us on 14th August since he is on leave."],
    ["", "Switchback", "Branding", "Ally", "Anushri", "9819877308", "anushri20@gmail.com", "Commercials", "₹1,500,000.00", "", "This is cold atm"],
    ["", "Ride Glyde", "Branding", "Ally", "Vignesh", "9136960544", "vignesh@rideglyde.in", "Commercials", "₹1,500,000.00", "", "Client pushing marketing a bit for now, focusing on finalising operations."],
    ["", "Kimirica", "Branding", "Ally", "Saomya", "9893060926", "soamya.mital@kimirica.com", "Commercials", "₹1,500,000.00", "", "On hold atm"],
    ["", "Messe Muenchen", "Branding", "Ally", "Riddhi", "7517998999", "support.marcom@mm-india.in", "Didnt work out", "₹1,800,000.00", "", "Client is not responding"],
    ["", "Vanveda Organics", "Branding", "Ally", "Chandan", "7517998999", "support.marcom@mm-india.in", "Didnt work out", "₹850,000.00", "", "Update to be received by this weekend. 9-10th August"],
    ["", "Pepsodent", "Branding", "Tan", "Reshma", "99302 99445", "reshma.vaidya@unilever.com", "Closed", "₹1,000,000.00", "", "Project completed."],
    ["", "Zydus Cadila", "Branding", "Tan", "Yash", "98697 31997", "YASHL.GANDHI@zyduslife.com", "Didnt work out", "₹700,000.00", "", "They ghosted us."],
    ["", "Unomax", "Branding", "Ally", "Sajad", "", "sajjad.godhrawala@unomaxpens.com", "Didnt work out", "₹500,000.00", "", "Closed on an industrial design agency"],
    ["", "Sports Nutrition Brand", "Branding", "Ally", "Shabnam", "97268 82211", "Shabnamhalani8@gmail.com", "Commercials", "₹1,150,000.00", "", "Follow up done client will get back post the long weekend"],
    ["", "Speedex", "Branding", "Ally", "Dewakar", "9911202317", "brandmarketer@speedexind.com", "Commercials", "₹1,000,000.00", "", "Pitch on 26th August"],
    ["", "Scapes Hospitality", "SMM, Web", "Tan", "Aastha", "8130001729", "aastha@scapeshospitality.com", "Commercials", "", "", "Project was on hold."],
    ["", "Cafe Branding", "Branding", "Ally", "Sharon", "9930656794", "sharon22193@gmail.com", "Didnt work out", "₹500,000.00", "", "Branding proposal shared. Client is reviewing it at their end"],
    ["", "Horizon Tech Park", "Coffee table Book", "Ally", "", "", "ronnie.Zaiwalla@hiparks.com", "", "₹500,000.00", "", "Branding proposal and references shared for the brochure."],
    ["", "HOF", "Branding", "Ally", "Somendra", "9904304513", "somendra@hofindia.com", "Didnt work out", "₹900,000.00", "", "Branding proposal shared. Client is reviewing it at their end"],
    ["", "South Indian Restaurant", "Branding", "Ally", "Shashank", "8825202574", "shashanksauravv@gmail.com", "Didnt work out", "TBD", "", "Client will call back"],
    ["", "Pantaloons", "Branding", "Ally", "Namit", "8879502010", "namit.jaiswal@abfrl.adityabirla.com", "Pitch", "TBD", "", "Rate card has been shared with the client. Client to get back"],
    ["", "XOBO", "Branding", "Ally", "Kunal", "9960100100", "kunaljain.vega@gmail.com", "Pitch", "", "", "Proposal under review."],
    ["", "Indo Atma", "Branding", "Ally", "Arastu", "5617597364", "arastu@indoatma.com", "Didnt work out", "", "", "Client has gone silent on the NDA front."],
    ["", "Komyo Wellness", "Web", "Ally", "Aditi", "9811029230", "aditi@Komyo.in", "Commercials", "", "", "Client to get back on the proposal"],
    ["", "KKings Events", "Branding", "Ally", "Ketan", "", "ketan@kkingsevents.com", "Commercials", "₹1,300,000.00", "", "Proposal shared client to revert on the same."],
    ["", "Kaafi Machine", "Branding", "Ally", "Anurag", "", "anurag.das@kaapimachines.com", "Pitch", "TBD", "", "Anurag to get back on the call timing"],
    ["", "House of Swadehi", "Branding", "Ally", "", "", "houseofswadeshiofficial@gmail.com", "First Call", "TBD", "", "Have requested for a call time to discuss the Logo development project."],
    ["", "Saanya", "Web", "Ally", "", "9310000663", "saanyabjain@gmail.com", "First Call", "TBD", "", "She wants to see the backend work on the developer"],
    ["", "Ruloans", "Campaign", "Ally", "Shikha", "", "shikha.mehta@ruloans.com", "Commercials", "TBD", "", "In-person meet at the client office"],
    ["", "Humane World For Animals", "Creatives", "Ally", "Shreya", "6358913490", "sswaminath@humaneworld.org", "First Call", "TBD", "", "revised proposal to be shared for print and outdoor"],
    ["", "Anahata", "", "Ally", "Cecilia", "9820533332", "admin@anahata.in", "First Call", "", "", "she will call back"],
    ["", "Hamleys Cafe", "Campaign", "Ally", "Bala", "9820964012", "sivaraman.B@ril.com", "Closed", "₹200,000.00", "", "Hamleys Cafe Logo and Guidelines"],
    ["", "Sambhav Group", "Web", "Tan", "Megha", "90049 86631", "media@sambhavgroup.co.in", "Commercials", "", "", "Project was on hold."],
    ["", "Cool Planet", "Branding", "Ally", "Rizqi", "94777653936", "qi@coolplanet.lk", "Commercials", "TBD", "", ""],
    ["", "Voltas", "Branding", "Tan", "Gayathri", "96006 56773", "gayathrinarendran@voltas.com", "First Call", "", "", "Client ghosted us."],
    ["", "A Class Marble", "Web", "Tan", "Shivani", "72900 73527", "branding@aclassmarble.co.in", "Commercials", "", "", "Project on hold"],
    ["", "Dynamic Engineering", "Branding", "Ally", "Sehej", "9930564146", "info@dynamicengineeringcompany.com", "Didnt work out", "", "", "Cost of 3L"],
    ["", "Rameswaram cafe", "Branding", "Tan", "Pooja", "89281 91088", "pooja.u@seabird.co.in", "Commercials", "", "", "They ghosted us."],
    ["", "Sony Music", "Branding", "Ally", "Samarth", "7722036793", "samarth.manocha@sonymusic.com", "Commercials", "", "", "Proposal shared. Client to get back"],
    ["", "ECCO", "Branding", "Ally", "Inza", "9619340027", "INN@ecco.com", "Commercials", "", "", "Revised proposal discussion to happen basis the deliverables requested by the client."],
    ["", "Upadhyaya Foundation", "Branding", "Ally", "Preetham", "9483780058", "preetham@upadhyayafoundation.org", "Commercials", "", "", "Proposal shared with the client."],
    ["", "Ice Cream Brand", "Branding", "Ally", "Dharmesh", "7907487352", "hnmpltd@outlook.com", "Didnt work out", "", "", "Budget of 2L"],
    ["", "Dainik Bhaskar Pet Care", "Branding", "Tan", "Diva", "-", "diva@dbdigital.in", "First Call", "", "", "Ghosted us because of commercials I guess"],
    ["", "Dove", "Branding", "Tan", "Manasee", "98676 42764", "manasee.naik@unilever.com", "Closed", "₹150,000.00", "", "Project completed"],
    ["", "Pears", "Branding", "Tan", "Manasee", "98676 42764", "manasee.naik@unilever.com", "Closed", "₹150,000.00", "", "Project completed"],
    ["", "Everfruit", "Branding", "Ally", "Piyush", "9561621164", "piyush.parakh@everfruit.in", "Commercials", "", "", "Proposal shared with the client."],
    ["", "Hindustan Times", "Branding", "Ally", "Srashti", "8717878891", "srashti.jain@hindustantimes.com", "Didnt work out", "", "", "Badge and Trophy design costing shared with the client."],
    ["", "Big FM", "Branding", "Ally", "Soha", "9990590444", "akanksha.goel@weinvert.com", "Commercials", "", "", "RFP shared with the client."],
    ["", "Amaya", "Web", "Ally", "Akshi", "9643122358", "aakshi.katyal@gmail.com", "Commercials", "", "", "Proposal and pitch for the 24th October."],
    ["", "Peruh", "Branding", "Tan", "Prerna", "", "prerna@peruhworld.com", "First Call", "", "", "Ghosted us"],
    ["", "Pump Manufacturer", "Branding", "Ally", "Nik", "3468528114", "nikp09528@gmail.com", "Didnt work out", "", "", "CTR on the proposal shared"],
    ["", "Jawa", "Branding", "Ally", "Samir Gokhale", "9921003800", "gokhale.samir@classiclegends.com", "First Call", "", "", "Blueprint to be shared with the client basis the last pitch"],
    ["", "Volfsbane", "Web", "Ally", "Mansi", "", "mansi@volfsbane.com", "Commercials", "", "", "Website branding proposal shared. Awaiting response."],
    ["", "Haldirams", "Branding", "Ally", "Bhagyashree", "9619342495", "bhagyashree.paralkar@haldirams.com", "Didnt work out", "", "", "Proposal to be shared post closure on social media"],
    ["", "Asian Star", "Branding", "Ally", "Ryan", "9820507257", "ryan@asianstargroup.com", "First Call", "", "", "CTR back on the proposal shared"],
    ["", "Samarya", "Branding", "Ally", "Aryan", "9137809177", "aryan.ruia@samaryamedia.com", "Commercials", "", "", "Logo Design Proposal shared with the client."],
    ["", "Seedwater", "Branding", "Ally", "Vivek", "9819711218", "vivek@seedwtr.com", "Commercials", "", "", "CTR on the proposal shared"],
    ["", "Quartroloom", "Branding", "Ally", "Avase", "8867658800", "avase@quartoloom.com", "Commercials", "", "", "CTR on the proposal shared"],
    ["", "Rajhem Jewellers", "Branding", "Ally", "Ritik", "9515311755", "ritikjain23112@gmail.com", "Commercials", "", "", "CTR on the proposal shared"],
    ["", "Wellness Brand", "Branding", "Ally", "Ruchi", "7350889295", "ruchi.pandit2008@gmail.com", "Commercials", "", "", "Client will get back with the numbers they want to close on today."],
    ["", "O Source Global", "Web", "Tan", "Durvanka", "96194 33680", "durvanka.murkute@osourceglobal.com", "Commercials", "", "", "Commercials didn't work"],
    ["", "EuroKids", "Web", "Tan", "Rakesh", "97737 73230", "rakesh.baikar@lighthouse-learning.com", "Commercials", "", "", "Ghosted us"],
    ["", "Sanjeev (Healthy Snacks)", "Branding", "Ally", "Sanjeev", "9815338888", "sb@sbhind.com", "First Call", "", "", "Proposal under review."],
    ["", "Worthvial", "Branding", "Ally", "Rohit", "9013232346", "rohit@worthvial.com", "Commercials", "", "", "Client will get back with the numbers they want to close on today."],
    ["", "Bellagio", "Branding", "Ally", "Arya", "9013232346", "aryaadak2000@gmail.com", "Commercials", "", "", "Client meeting on the 12th Jan, 2026"],
    ["", "Granotone", "Branding", "Tan", "Sarthak", "97600 32125", "sarthak@granotone.com", "Commercials", "", "", "Ghosted us."],
    ["", "Nuvoco", "Branding", "Ally", "Nikhil", "9702036462", "Nikhil.Sukthankar@nuvoco.com", "Pitch", "", "", "Pitch done. RFQ will be shared with us this week."],
    ["", "Kids Infotainment", "Branding", "Tan", "Mazahir", "90221 22928", "", "First Call", "", "", "He ghosted us"],
    ["", "Zune Clothing", "Branding", "Tan", "Shivam", "75056 43933", "shivamyadav9258@gmail.com", "Didnt work out", "", "", "Had very low budgets, 2L for branding."],
    ["", "Luxury Bags", "Branding", "Ally", "Ayesha", "9619077701", "NA", "Didnt work out", "", "", "Low budget client."],
    ["", "HOS Global Foods", "Branding", "Ally", "Shruti", "8879433104", "skulkarni@houseofspicesindia.com", "Didnt work out", "", "", "Client has mentioned they will work on future projects with us."],
    ["", "Els Hair", "Web", "Ally", "Simran", "8383008876", "work.skataria@gmail.com", "Didnt work out", "", "", "No response post proposal for website revamp shared with the client."],
    ["", "Ageasy", "Branding", "Ally", "Arushi", "9013492656", "arushi.aggarwal@antaraseniorcare.com", "Closed", "₹400,000.00", "", "Proposal shared with the client for review and approval"],
    ["", "Cello", "Branding", "Ally", "Suresh", "", "suresh.amarnani@celloworld.com", "Commercials", "", "", "Proposal has been shared. No response."],
    ["", "Inorbit", "Branding", "Ally", "Tiyasha", "9674119228", "tiyasha.mitra@inorbit.in", "Didnt work out", "", "", "Case Studies deck shared with the client."],
    ["14th Jan", "HueTag", "Branding", "Tan", "Yash", "9643634608", "Yash.lakhmani0580@gmail.com", "First Call", "", "", "commercials didn't work"],
    ["19th Jan", "Oral-care FMCG brand", "Branding", "Ally", "Harshleen", "9575100999", "bhatiaharshleen11@gmail.com", "Didnt work out", "TBD", "", "Client has not responded to calls and texts."],
    ["", "Elevator Brand", "Branding", "Ally", "Prachi", "7738387212", "prachi.jadhav@eroselevators.com", "Didnt work out", "TBD", "", "Commercials shared with the client. Client has not responded thereafter."],
    ["22nd Jan", "Project Ezza", "Branding, Web", "Ally", "Dimpy", "9920274266", "", "Commercials", "550000", "", "Proposal has been shared with the client for website."],
    ["28th Jan", "My Athlete", "Branding", "Ally", "Bhaben", "9792674222", "bhaben83@gmail.com", "Didnt work out", "TBD", "", "Proposal to be shared for the same by the 29th January, 2026"],
    ["", "Forge Tech", "Branding", "Ally", "Prasad", "7208482730", "prasad.kabadi@ideaforgetech.com", "First Call", "TBD", "", "Tried connecting with the client but was not able to get through."],
    ["", "Punjas", "Branding", "Ally", "Gopal", "6797008805", "gopal@punjas.com", "Commercials", "", "", "Rate card shared with the client."],
    ["", "NA", "Branding", "Tan", "Falguni", "88799 27537", "falguni240396@gmail.com", "Commercials", "", "", "commercials didn't work"],
    ["", "Biorad", "Branding", "Ally", "Tanishq", "61 0451991409", "tanishq.hegde@bioradmedisys.com", "First Call", "", "", "Proposal commercials closure call at 1 pm."],
    ["29th Jan", "Pureforma", "Branding", "Ally", "Pratima", "9892902338", "pratima.kamat@pureforma.in", "First Call", "", "", "First call done with the client."],
    ["", "Oilmax", "Branding", "Ally", "Rostan", "9960287807", "rostan.miranda@aniritventures.com", "Commercials", "", "", "Proposal has been shared with the client. Awaiting response on the same."],
    ["", "Kimora", "Branding", "Ally", "Bhumi", "9510070153", "business@kimora.in", "Commercials", "", "", "Internal review of budgets ongoing."],
    ["12th Feb", "Organic Food Brand", "Branding", "Tan", "Yashraj", "9698691111", "yashrajsinghtada@gmail.com", "First Call", "₹1,000,000.00", "", "Yashraj has a budget of 7L for branding and packaging."],
    ["12th Feb", "Coffee Branding", "Branding", "Tan", "Shreyansh", "99872 48272", "doshi.shreyansh@gmail.com", "Commercials", "", "", "Sent him a proposal for 22L, awaiting to hear back"],
    ["16th Feb", "Automobile brand", "Branding", "Tan", "Dhrumil", "91670 76010", "dhrumil@dhcindia.com", "Commercials", "", "", "Have sent him our commercials"],
    ["17th Feb", "SBI MF", "Creatives", "Tan", "Prachi", "9599407143", "prachi.shinde@sbimf.com", "First Call", "", "", ""],
    ["17th Feb", "Powerbuild Batteries", "Branding", "Ally", "Pawan", "8983350003", "pawan.lahane@timetechnoplast.com", "Commercials", "", "", "Proposal shared for review. Awaiting response on the same."],
    ["18th Feb", "Kimirica", "Branding", "Ally", "Pooja", "9584000357", "pooja.bhagat@kimirica.shop", "Commercials", "", "", "Mall Pop Up Moodboard commercials shared with the client. No response."],
    ["18th Feb", "Dada Design", "Web", "Ally", "Vasanthan", "974 51386864", "vasanth@dadaarchitecture.com", "Didnt work out", "", "", "No response. Follow up has been done."],
    ["2nd March", "Upal - Branding", "Branding", "Ally", "Upal", "9820173037", "upalsarkar31@gmail.com", "Didnt work out", "", "", "Budget of 2.5L."],
    ["2nd March", "Megrove Global School", "Branding", "Ally", "Amol", "9021496479", "amol.m@adccacademy.com", "Didnt work out", "", "", "Proposal discussion and commercials on the 25th Feb."],
    ["2nd March", "Ayvens India", "Branding", "Ally", "Shalini", "95822 14969", "shalini.baveja@ayvens.com", "Pitch", "", "", "Pitch date to be finalised basis the call."],
    ["2nd March", "Kimirica", "Web", "Ally", "Saloni", "9111 744 744", "saloni.saraf@kimirica.shop", "Commercials", "", "", "Proposal shared with the client."],
    ["9th March", "Kalatita + NGO", "Branding", "Ally", "Darayash", "919820060818", "darayash.gocal@gmail.com", "First Call", "", "", "Client is yet to confirm on the meeting in-office."],
    ["11th March", "Fabletics", "Branding", "Tan", "Roshni", "95799 39636", "", "Commercials", "₹300,000.00", "", "Need to send the proposal today."],
]


# ── Data Processing Helpers ──

def parse_cost(val):
    """Parse a cost string to a number. Returns None for TBD/empty."""
    if val is None or val == "":
        return None
    if isinstance(val, (int, float)):
        return val
    s = str(val).strip()
    if s in ("-", "") or s.lower() in ("tbd", "cost to be decided"):
        return s  # Keep as string marker
    # Strip ₹, Rs, spaces, commas
    cleaned = re.sub(r'[₹Rs.\s]', '', s, flags=re.IGNORECASE)
    cleaned = cleaned.replace(',', '')
    m = re.search(r'(\d+\.?\d*)', cleaned)
    if m:
        return float(m.group(1))
    return s  # Return original if unparseable


def standardize_phone(phone):
    """Standardize Indian phone numbers to +91 XXXXX XXXXX format."""
    if not phone or phone == "-" or phone.lower() == "not available":
        return phone
    digits = re.sub(r'\D', '', str(phone))
    if not digits:
        return phone
    if len(digits) == 10 and digits[0] in '6789':
        return f"+91 {digits[:5]} {digits[5:]}"
    if len(digits) == 11 and digits[0] == '0':
        digits = digits[1:]
        return f"+91 {digits[:5]} {digits[5:]}"
    if len(digits) == 12 and digits[:2] == '91':
        return f"+91 {digits[2:7]} {digits[7:]}"
    if len(digits) == 13 and digits[:3] == '919':
        return f"+91 {digits[2:7]} {digits[7:]}"
    # International or unusual
    return f"+{digits}"


def process_data(raw):
    """Clean all data rows. Returns list of processed rows."""
    processed = []
    for row in raw:
        new_row = list(row)
        # Clean phone (col 5, index 5)
        new_row[5] = standardize_phone(new_row[5])
        # Clean email (col 6, index 6) - strip whitespace
        new_row[6] = str(new_row[6]).strip() if new_row[6] else ""
        # Clean cost (col 8, index 8)
        new_row[8] = parse_cost(new_row[8])
        processed.append(new_row)
    return processed


# ── Sheet Builders ──

def write_header(ws, headers):
    """Write and format header row."""
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.freeze_panes = "A2"


def auto_width(ws, data_rows, headers):
    """Set column widths based on content."""
    widths = {i + 1: len(h) + 2 for i, h in enumerate(headers)}
    for row in data_rows:
        for i, val in enumerate(row):
            w = len(str(val)) + 2 if val else 0
            col = i + 1
            if col in widths:
                widths[col] = min(max(widths[col], w), 40)  # Cap at 40
    for col, w in widths.items():
        ws.column_dimensions[get_column_letter(col)].width = w


def write_data_rows(ws, data, start_row=2, alt_colors=True):
    """Write data rows with optional alternating colors."""
    for i, row in enumerate(data):
        excel_row = start_row + i
        for j, val in enumerate(row):
            cell = ws.cell(row=excel_row, column=j + 1)
            # Write value
            if val is None:
                cell.value = ""
            elif isinstance(val, (int, float)):
                cell.value = val
                if j == 8:  # Costs column
                    cell.number_format = CURRENCY_FMT
            else:
                cell.value = str(val)
            cell.border = THIN_BORDER
        # Alternating row color
        if alt_colors and i % 2 == 1:
            for j in range(len(row)):
                ws.cell(row=excel_row, column=j + 1).fill = ALT_ROW_FILL


def build_pipeline_sheet(wb, data):
    """Build the main Pipeline sheet with data, validation, and formatting."""
    ws = wb.active
    ws.title = "Pipeline"
    ws.sheet_properties.tabColor = "1A237E"

    write_header(ws, HEADERS)
    write_data_rows(ws, data)
    auto_width(ws, data, HEADERS)

    last_row = len(data) + 1

    # Auto-filter
    ws.auto_filter.ref = f"A1:K{last_row}"

    # Data validation: Stage (column H)
    stage_dv = DataValidation(
        type="list",
        formula1='"' + ','.join(STAGES) + '"',
        allow_blank=True
    )
    stage_dv.error = "Please select a valid stage"
    stage_dv.errorTitle = "Invalid Stage"
    stage_dv.prompt = "Select the deal stage"
    stage_dv.promptTitle = "Stage"
    ws.add_data_validation(stage_dv)
    stage_dv.add(f"H2:H{last_row}")

    # Data validation: Handler (column D)
    handler_dv = DataValidation(
        type="list",
        formula1='"' + ','.join(HANDLERS) + '"',
        allow_blank=True
    )
    handler_dv.error = "Please select a valid handler"
    handler_dv.errorTitle = "Invalid Handler"
    ws.add_data_validation(handler_dv)
    handler_dv.add(f"D2:D{last_row}")

    # Conditional formatting: Stage = "Closed" → green
    ws.conditional_formatting.add(
        f"H2:H{last_row}",
        CellIsRule(operator="equal", formula=['"Closed"'], fill=GREEN_FILL)
    )
    # Stage = "Didnt work out" → red
    ws.conditional_formatting.add(
        f"H2:H{last_row}",
        CellIsRule(operator="equal", formula=['"Didnt work out"'], fill=RED_FILL)
    )
    # Stage = "Commercials" → yellow
    ws.conditional_formatting.add(
        f"H2:H{last_row}",
        CellIsRule(operator="equal", formula=['"Commercials"'], fill=YELLOW_FILL)
    )
    # Stage = "Pitch" → orange
    ws.conditional_formatting.add(
        f"H2:H{last_row}",
        CellIsRule(operator="equal", formula=['"Pitch"'], fill=ORANGE_FILL)
    )

    # Empty phone (F) → red highlight
    ws.conditional_formatting.add(
        f"F2:F{last_row}",
        FormulaRule(formula=[f'LEN(TRIM(F2))=0'], fill=RED_FILL)
    )
    # Empty email (G) → red highlight
    ws.conditional_formatting.add(
        f"G2:G{last_row}",
        FormulaRule(formula=[f'LEN(TRIM(G2))=0'], fill=RED_FILL)
    )

    # Cost column formatting
    for r in range(2, last_row + 1):
        cell = ws.cell(row=r, column=9)
        if isinstance(cell.value, (int, float)):
            cell.number_format = CURRENCY_FMT

    return ws


def build_dashboard(wb, data):
    """Build the Dashboard sheet with live formulas."""
    ws = wb.create_sheet("Dashboard")
    ws.sheet_properties.tabColor = "FF9800"

    r = 1

    # Title
    ws.merge_cells("A1:F1")
    title_cell = ws.cell(row=r, column=1, value="PIPELINE DASHBOARD")
    title_cell.font = TITLE_FONT
    title_cell.fill = HEADER_FILL
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    r += 1

    ws.cell(row=r, column=1, value="Formulas update automatically when Pipeline data changes").font = Font(italic=True, color="666666")
    r += 2

    # ── Pipeline Summary by Stage ──
    ws.merge_cells(f"A{r}:D{r}")
    ws.cell(row=r, column=1, value="PIPELINE SUMMARY BY STAGE").font = SECTION_FONT
    for c in range(1, 5):
        ws.cell(row=r, column=c).fill = SECTION_FILL
    r += 1

    sub_headers = ["Stage", "Count", "Total Value", "Avg Deal Size"]
    for c, h in enumerate(sub_headers, 1):
        cell = ws.cell(row=r, column=c, value=h)
        cell.font = BOLD_FONT
        cell.fill = SUBHEADER_FILL
    r += 1

    stage_start_row = r
    for stage in STAGES:
        ws.cell(row=r, column=1, value=stage)
        ws.cell(row=r, column=2).value = f'=COUNTIF(Pipeline!H:H,"{stage}")'
        ws.cell(row=r, column=3).value = f'=SUMIF(Pipeline!H:H,"{stage}",Pipeline!I:I)'
        ws.cell(row=r, column=3).number_format = CURRENCY_FMT
        ws.cell(row=r, column=4).value = f'=IFERROR(C{r}/B{r},0)'
        ws.cell(row=r, column=4).number_format = CURRENCY_FMT
        r += 1

    # Totals row
    ws.cell(row=r, column=1, value="TOTAL").font = BOLD_FONT
    ws.cell(row=r, column=2).value = f'=SUM(B{stage_start_row}:B{r - 1})'
    ws.cell(row=r, column=2).font = BOLD_FONT
    ws.cell(row=r, column=3).value = f'=SUM(C{stage_start_row}:C{r - 1})'
    ws.cell(row=r, column=3).font = BOLD_FONT
    ws.cell(row=r, column=3).number_format = CURRENCY_FMT
    ws.cell(row=r, column=4).value = f'=IFERROR(C{r}/B{r},0)'
    ws.cell(row=r, column=4).font = BOLD_FONT
    ws.cell(row=r, column=4).number_format = CURRENCY_FMT
    total_row = r
    r += 2

    # ── Revenue Metrics ──
    ws.merge_cells(f"A{r}:B{r}")
    ws.cell(row=r, column=1, value="REVENUE METRICS").font = SECTION_FONT
    ws.cell(row=r, column=1).fill = SECTION_FILL
    ws.cell(row=r, column=2).fill = SECTION_FILL
    r += 1

    metrics = [
        ("Closed Revenue", '=SUMIF(Pipeline!H:H,"Closed",Pipeline!I:I)'),
        ("Active Pipeline Value", '=SUMIF(Pipeline!H:H,"First Call",Pipeline!I:I)+SUMIF(Pipeline!H:H,"Pitch",Pipeline!I:I)+SUMIF(Pipeline!H:H,"Commercials",Pipeline!I:I)'),
        ("Total Pipeline (excl. Lost)", f'=B{r}+B{r + 1}'),
        ("Average Deal Size", f'=IFERROR(C{total_row}/B{total_row},0)'),
        ("Deals with TBD Costs", '=COUNTIF(Pipeline!I:I,"TBD")'),
    ]
    for label, formula in metrics:
        ws.cell(row=r, column=1, value=label).font = BOLD_FONT
        ws.cell(row=r, column=2).value = formula
        if label != "Deals with TBD Costs":
            ws.cell(row=r, column=2).number_format = CURRENCY_FMT
        r += 1
    r += 1

    # ── Team Performance ──
    ws.merge_cells(f"A{r}:E{r}")
    ws.cell(row=r, column=1, value="TEAM PERFORMANCE").font = SECTION_FONT
    for c in range(1, 6):
        ws.cell(row=r, column=c).fill = SECTION_FILL
    r += 1

    team_headers = ["Team Member", "Total Deals", "Closed", "Closing Rate", "Revenue"]
    for c, h in enumerate(team_headers, 1):
        cell = ws.cell(row=r, column=c, value=h)
        cell.font = BOLD_FONT
        cell.fill = SUBHEADER_FILL
    r += 1

    for handler in HANDLERS:
        ws.cell(row=r, column=1, value=handler)
        ws.cell(row=r, column=2).value = f'=COUNTIF(Pipeline!D:D,"{handler}")'
        ws.cell(row=r, column=3).value = f'=COUNTIFS(Pipeline!D:D,"{handler}",Pipeline!H:H,"Closed")'
        ws.cell(row=r, column=4).value = f'=IFERROR(C{r}/B{r},0)'
        ws.cell(row=r, column=4).number_format = PCT_FMT
        ws.cell(row=r, column=5).value = f'=SUMIFS(Pipeline!I:I,Pipeline!D:D,"{handler}",Pipeline!H:H,"Closed")'
        ws.cell(row=r, column=5).number_format = CURRENCY_FMT
        r += 1
    r += 1

    # ── Scope Breakdown ──
    ws.merge_cells(f"A{r}:C{r}")
    ws.cell(row=r, column=1, value="SCOPE TYPE BREAKDOWN").font = SECTION_FONT
    for c in range(1, 4):
        ws.cell(row=r, column=c).fill = SECTION_FILL
    r += 1

    scope_headers = ["Scope Type", "Count", "Value"]
    for c, h in enumerate(scope_headers, 1):
        cell = ws.cell(row=r, column=c, value=h)
        cell.font = BOLD_FONT
        cell.fill = SUBHEADER_FILL
    r += 1

    for scope in SCOPES:
        ws.cell(row=r, column=1, value=scope)
        ws.cell(row=r, column=2).value = f'=COUNTIF(Pipeline!C:C,"*{scope}*")'
        ws.cell(row=r, column=3).value = f'=SUMIF(Pipeline!C:C,"*{scope}*",Pipeline!I:I)'
        ws.cell(row=r, column=3).number_format = CURRENCY_FMT
        r += 1

    # Auto-width
    ws.column_dimensions['A'].width = 30
    ws.column_dimensions['B'].width = 18
    ws.column_dimensions['C'].width = 18
    ws.column_dimensions['D'].width = 18
    ws.column_dimensions['E'].width = 18

    return ws


def build_stage_sheet(wb, name, data, tab_color, filter_fn):
    """Build a filtered stage sheet."""
    ws = wb.create_sheet(name)
    ws.sheet_properties.tabColor = tab_color

    filtered = [row for row in data if filter_fn(row)]
    # Sort by cost descending (numeric costs first, then non-numeric)
    filtered.sort(key=lambda r: r[8] if isinstance(r[8], (int, float)) else -1, reverse=True)

    write_header(ws, HEADERS)
    write_data_rows(ws, filtered)
    auto_width(ws, filtered, HEADERS)

    if filtered:
        last_row = len(filtered) + 1
        ws.auto_filter.ref = f"A1:K{last_row}"

    return ws


# ── Main ──

def main():
    print("Processing pipeline data...")
    data = process_data(RAW_DATA)

    print("Creating workbook...")
    wb = Workbook()

    # Sheet 1: Pipeline
    print("  Building Pipeline sheet...")
    build_pipeline_sheet(wb, data)

    # Sheet 2: Dashboard
    print("  Building Dashboard sheet...")
    build_dashboard(wb, data)

    # Sheet 3: Closed Deals
    print("  Building Closed Deals sheet...")
    build_stage_sheet(wb, "Closed Deals", data, "4CAF50",
                      lambda r: str(r[7]).strip() == "Closed")

    # Sheet 4: Active Pipeline
    print("  Building Active Pipeline sheet...")
    build_stage_sheet(wb, "Active Pipeline", data, "2196F3",
                      lambda r: str(r[7]).strip() in ACTIVE_STAGES)

    # Sheet 5: Lost Deals
    print("  Building Lost Deals sheet...")
    build_stage_sheet(wb, "Lost Deals", data, "F44336",
                      lambda r: str(r[7]).strip() == "Didnt work out")

    # Save
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "Pipeline_Tracker.xlsx")

    wb.save(output_path)
    print(f"\nDone! File saved to: {output_path}")
    print(f"  - Pipeline: {len(data)} rows")
    print(f"  - Closed Deals: {sum(1 for r in data if str(r[7]).strip() == 'Closed')} rows")
    print(f"  - Active Pipeline: {sum(1 for r in data if str(r[7]).strip() in ACTIVE_STAGES)} rows")
    print(f"  - Lost Deals: {sum(1 for r in data if str(r[7]).strip() == 'Didnt work out')} rows")
    print(f"  - Dashboard: live formulas (auto-updates)")


if __name__ == "__main__":
    main()
