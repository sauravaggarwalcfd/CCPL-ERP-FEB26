"""Google Sheets service layer for Dyeing BOM module.
Ported from BOM-main project - replicates CODE.GS functionality.
"""
import os
from datetime import datetime
from typing import List, Optional, Dict, Any

from ..config import settings
from ..models.bom import (
    Article, MasterArticle, Color, FabricQuality, MasterData,
    BOMLine, Combo, BOMHeader, BOM, BOMIndexItem, DyeingPlan
)

# Try to import Google libraries
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


class SheetsService:
    """Service for interacting with Google Sheets."""

    # Sheets to skip when listing articles
    SKIP_SHEETS = [
        'MASTER DATA', 'Automation', 'W 25 LOT WISE DETAIL', 'FABRIC MASTERDATA',
        'details', 'Planning', 'ARTWISE QTY', 'DUMMY', 'EXTRA',
        '1. PLNG W0 SHRTG', '2. PLNG WITH SHRTG', '3. YRN RQSN',
        '4. PLNG WITH SHRTG ARTWISE', '5. PLNG WITH SHRTG CLR WISE',
        'for r2 1', 'for r2 2', 'R2', '6. SHRINKAGE REPORT',
        '7. DYEING LOT STATUS REPORT (AR', '8. LOTS STATUS REPORT (COLOR WI',
        '9. LOTS STATUS REPORT (COLOR WI', '10. FABRIC TRACKING REPORT',
        'BOM_INDEX', 'BOM_DATA', 'DPLAN_INDEX'
    ]

    def __init__(self):
        self.spreadsheet_id = settings.BOM_SPREADSHEET_ID
        self.service = None
        self.demo_mode = False
        self.error_message = None

        # Check if we should use demo mode
        if not settings.BOM_SPREADSHEET_ID or settings.BOM_SPREADSHEET_ID == "your_spreadsheet_id_here":
            self.demo_mode = True
            self.error_message = "Spreadsheet ID not configured. Running in DEMO MODE."
            return

        if not GOOGLE_AVAILABLE:
            self.demo_mode = True
            self.error_message = "Google API libraries not installed. Running in DEMO MODE."
            return

        # Initialize Google Sheets API
        creds_path = settings.BOM_GOOGLE_CREDENTIALS_PATH
        if not os.path.exists(creds_path):
            self.demo_mode = True
            self.error_message = f"credentials.json not found at '{creds_path}'. Running in DEMO MODE."
            return

        try:
            creds = service_account.Credentials.from_service_account_file(
                creds_path,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            self.service = build('sheets', 'v4', credentials=creds)
        except Exception as e:
            self.demo_mode = True
            self.error_message = f"Failed to initialize Google Sheets: {str(e)}. Running in DEMO MODE."

    def _get_sheet(self):
        """Get sheets API resource."""
        if self.demo_mode:
            raise Exception(self.error_message or "Running in demo mode")
        if not self.service:
            raise Exception("Google Sheets not configured. Add credentials.json")
        return self.service.spreadsheets()

    def _get_values(self, range_name: str) -> List[List[Any]]:
        """Get values from a range."""
        result = self._get_sheet().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=range_name
        ).execute()
        return result.get('values', [])

    def _update_values(self, range_name: str, values: List[List[Any]]):
        """Update values in a range."""
        self._get_sheet().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body={'values': values}
        ).execute()

    def _append_values(self, range_name: str, values: List[List[Any]]):
        """Append values to a sheet."""
        self._get_sheet().values().append(
            spreadsheetId=self.spreadsheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body={'values': values}
        ).execute()

    def _clear_range(self, range_name: str):
        """Clear a range."""
        self._get_sheet().values().clear(
            spreadsheetId=self.spreadsheet_id,
            range=range_name
        ).execute()

    def _get_all_sheets(self) -> List[str]:
        """Get all sheet names in the spreadsheet."""
        result = self._get_sheet().get(spreadsheetId=self.spreadsheet_id).execute()
        return [s['properties']['title'] for s in result.get('sheets', [])]

    def _sheet_exists(self, name: str) -> bool:
        """Check if a sheet exists."""
        return name in self._get_all_sheets()

    def _create_sheet(self, name: str):
        """Create a new sheet."""
        request = {'addSheet': {'properties': {'title': name}}}
        self._get_sheet().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body={'requests': [request]}
        ).execute()

    def _copy_sheet(self, source_name: str, dest_name: str):
        """Copy a sheet to a new name."""
        result = self._get_sheet().get(spreadsheetId=self.spreadsheet_id).execute()
        source_id = None
        for s in result.get('sheets', []):
            if s['properties']['title'] == source_name:
                source_id = s['properties']['sheetId']
                break

        if source_id is None:
            raise Exception(f"Sheet '{source_name}' not found")

        copy_request = {'destinationSpreadsheetId': self.spreadsheet_id}
        copy_result = self._get_sheet().sheets().copyTo(
            spreadsheetId=self.spreadsheet_id,
            sheetId=source_id,
            body=copy_request
        ).execute()

        new_sheet_id = copy_result['sheetId']
        rename_request = {
            'updateSheetProperties': {
                'properties': {'sheetId': new_sheet_id, 'title': dest_name},
                'fields': 'title'
            }
        }
        self._get_sheet().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body={'requests': [rename_request]}
        ).execute()

    # ============ DEMO DATA ============

    def _get_demo_master_data(self) -> MasterData:
        """Return demo data for testing."""
        return MasterData(
            articles=[
                Article(sheet_name="1307 HI", art_no="1307 HI", set_no="2609", season="SUMMER-2025", plan_qty=5000, buyer="DEMO BUYER"),
                Article(sheet_name="1405 PQ", art_no="1405 PQ", set_no="2610", season="SUMMER-2025", plan_qty=3000, buyer="DEMO BUYER"),
                Article(sheet_name="1502 RS", art_no="1502 RS", set_no="2611", season="WINTER-2025", plan_qty=4000, buyer="TEST BUYER"),
            ],
            colors=[
                Color(id="B91 / DESERT BROWN", code="B91", name="DESERT BROWN"),
                Color(id="979 / DRY GRASS", code="979", name="DRY GRASS"),
                Color(id="A12 / NAVY BLUE", code="A12", name="NAVY BLUE"),
                Color(id="C45 / OLIVE GREEN", code="C45", name="OLIVE GREEN"),
                Color(id="D78 / CHARCOAL", code="D78", name="CHARCOAL"),
            ],
            components=[
                "FR+BK+SLV+MOON+PKT+PLKT+NK TAPE",
                "COLLAR (17\")",
                "CUFF",
                "POCKET",
                "PLACKET",
            ],
            master_articles=[
                MasterArticle(art_no="1307 HI", sketch_link=""),
                MasterArticle(art_no="1405 PQ", sketch_link=""),
                MasterArticle(art_no="1502 RS", sketch_link=""),
            ],
            fabrics=[
                FabricQuality(quality="HONEYCOMB BOX KNIT 24'S P/C (20/80) 180GSM/68\"", unit="kg", avg_roll_size=25),
                FabricQuality(quality="FLAT COLLARS 17\"X3.25\"-36/42", unit="Pcs", avg_roll_size=100),
                FabricQuality(quality="SINGLE JERSEY 30'S COMBED 150GSM/72\"", unit="kg", avg_roll_size=25),
                FabricQuality(quality="RIB 1X1 30'S COMBED 200GSM/36\"", unit="kg", avg_roll_size=20),
            ]
        )

    def _get_demo_bom(self, sheet_name: str) -> BOM:
        """Return demo BOM data."""
        return BOM(
            header=BOMHeader(
                art_no=sheet_name,
                set_no="2609",
                season="SUMMER-2025",
                buyer="DEMO BUYER",
                plan_qty=5000,
                plan_date="2025-06-15",
                remarks="Demo BOM entry",
                sheet_name=sheet_name
            ),
            combos=[
                Combo(
                    combo_sr_no=1,
                    combo_name="DESERT BROWN",
                    color_id="B91 / DESERT BROWN",
                    color_code="B91",
                    color_name="DESERT BROWN",
                    plan_qty=3000,
                    bom_lines=[
                        BOMLine(
                            fabric_quality="HONEYCOMB BOX KNIT 24'S P/C (20/80) 180GSM/68\"",
                            plan_rat_gsm="180/68",
                            priority="1",
                            component="FR+BK+SLV+MOON+PKT+PLKT+NK TAPE",
                            avg=0.28,
                            unit="kg",
                            extra_pcs=0.1,
                            wastage_pcs=0.05,
                            shortage=0.1,
                            ready_fabric_need=966,
                            greige_fabric_need=1062.6
                        )
                    ]
                ),
                Combo(
                    combo_sr_no=2,
                    combo_name="DRY GRASS",
                    color_id="979 / DRY GRASS",
                    color_code="979",
                    color_name="DRY GRASS",
                    plan_qty=2000,
                    bom_lines=[
                        BOMLine(
                            fabric_quality="HONEYCOMB BOX KNIT 24'S P/C (20/80) 180GSM/68\"",
                            plan_rat_gsm="180/68",
                            priority="1",
                            component="FR+BK+SLV+MOON+PKT+PLKT+NK TAPE",
                            avg=0.28,
                            unit="kg",
                            extra_pcs=0.1,
                            wastage_pcs=0.05,
                            shortage=0.1,
                            ready_fabric_need=644,
                            greige_fabric_need=708.4
                        )
                    ]
                )
            ]
        )

    # ============ MASTER DATA FUNCTIONS ============

    def get_article_list(self) -> List[Article]:
        """Get list of articles from sheet tabs."""
        if self.demo_mode:
            return self._get_demo_master_data().articles

        articles = []
        sheets = self._get_all_sheets()

        for name in sheets:
            if name in self.SKIP_SHEETS or name.startswith('_'):
                continue

            try:
                plan_date = self._get_values(f"'{name}'!T1")
                plan_qty = self._get_values(f"'{name}'!W2")
                art_no = self._get_values(f"'{name}'!P2")
                set_no = self._get_values(f"'{name}'!P3")
                season = self._get_values(f"'{name}'!O1")
                buyer = self._get_values(f"'{name}'!W3")
                remarks = self._get_values(f"'{name}'!O5")

                pd_str = ""
                if plan_date and plan_date[0]:
                    pd_str = str(plan_date[0][0]) if plan_date[0][0] else ""

                pq_num = 0
                if plan_qty and plan_qty[0]:
                    try:
                        pq_num = float(plan_qty[0][0])
                    except:
                        pass

                articles.append(Article(
                    sheet_name=name,
                    art_no=str(art_no[0][0]) if art_no and art_no[0] else name,
                    set_no=str(set_no[0][0]) if set_no and set_no[0] else "",
                    season=str(season[0][0]) if season and season[0] else "",
                    plan_qty=pq_num,
                    buyer=str(buyer[0][0]) if buyer and buyer[0] else "",
                    plan_date=pd_str,
                    remarks=str(remarks[0][0]) if remarks and remarks[0] else ""
                ))
            except Exception as e:
                articles.append(Article(
                    sheet_name=name,
                    art_no=name,
                    remarks=f"Error reading: {str(e)}"
                ))

        return articles

    def get_components(self) -> List[str]:
        """Get unique components from MASTER DATA."""
        if self.demo_mode:
            return self._get_demo_master_data().components

        data = self._get_values("'MASTER DATA'!A2:A200")
        components = []
        for row in data:
            if row and row[0] and str(row[0]).strip():
                c = str(row[0]).strip()
                if c not in components:
                    components.append(c)
        return components

    def get_master_articles(self) -> List[MasterArticle]:
        """Get articles from MASTER DATA (Col I, J)."""
        if self.demo_mode:
            return self._get_demo_master_data().master_articles

        data = self._get_values("'MASTER DATA'!I2:J2500")
        articles = []
        seen = set()

        for row in data:
            if not row or not row[0] or not str(row[0]).strip():
                continue
            art_no = str(row[0]).strip()
            if art_no in seen:
                continue
            seen.add(art_no)

            sketch_link = str(row[1]).strip() if len(row) > 1 and row[1] else ""
            articles.append(MasterArticle(art_no=art_no, sketch_link=sketch_link))

        return articles

    def get_colors(self) -> List[Color]:
        """Get colors from MASTER DATA."""
        if self.demo_mode:
            return self._get_demo_master_data().colors

        data = self._get_values("'MASTER DATA'!C2:E500")
        colors = []

        for row in data:
            if len(row) >= 3 and row[2] and str(row[2]).strip():
                colors.append(Color(
                    id=str(row[0]).strip() if row[0] else "",
                    code=str(row[1]).strip() if row[1] else "",
                    name=str(row[2]).strip()
                ))

        return colors

    def get_fabric_qualities(self) -> List[FabricQuality]:
        """Get fabric qualities from FABRIC MASTERDATA."""
        if self.demo_mode:
            return self._get_demo_master_data().fabrics

        data = self._get_values("'FABRIC MASTERDATA'!A3:K3200")
        fabrics = []
        seen = set()

        for row in data:
            if len(row) >= 9 and row[8] and str(row[8]).strip():
                final_item = str(row[8]).strip()
                if final_item in seen:
                    continue
                seen.add(final_item)

                unit = str(row[10]).strip() if len(row) > 10 and row[10] else "kg"
                avg_roll = 25
                if len(row) > 9 and row[9]:
                    try:
                        avg_roll = float(row[9])
                    except:
                        pass

                fabrics.append(FabricQuality(
                    quality=final_item,
                    unit=unit,
                    avg_roll_size=avg_roll
                ))

        return fabrics

    def load_all_master_data(self) -> MasterData:
        """Load all master data in one call."""
        if self.demo_mode:
            return self._get_demo_master_data()

        return MasterData(
            articles=self.get_article_list(),
            colors=self.get_colors(),
            components=self.get_components(),
            master_articles=self.get_master_articles(),
            fabrics=self.get_fabric_qualities()
        )

    # ============ ARTICLE BOM FUNCTIONS ============

    def load_article_bom(self, sheet_name: str) -> BOM:
        """Load BOM data from an article sheet."""
        if self.demo_mode:
            return self._get_demo_bom(sheet_name)

        if not self._sheet_exists(sheet_name):
            raise Exception(f"Sheet not found: {sheet_name}")

        header_data = {
            'art_no': self._get_values(f"'{sheet_name}'!P2"),
            'set_no': self._get_values(f"'{sheet_name}'!P3"),
            'season': self._get_values(f"'{sheet_name}'!O1"),
            'plan_qty': self._get_values(f"'{sheet_name}'!W2"),
            'buyer': self._get_values(f"'{sheet_name}'!W3"),
            'plan_date': self._get_values(f"'{sheet_name}'!T1"),
            'remarks': self._get_values(f"'{sheet_name}'!O5"),
        }

        header = BOMHeader(
            art_no=str(header_data['art_no'][0][0]) if header_data['art_no'] and header_data['art_no'][0] else "",
            set_no=str(header_data['set_no'][0][0]) if header_data['set_no'] and header_data['set_no'][0] else "",
            season=str(header_data['season'][0][0]) if header_data['season'] and header_data['season'][0] else "",
            buyer=str(header_data['buyer'][0][0]) if header_data['buyer'] and header_data['buyer'][0] else "",
            remarks=str(header_data['remarks'][0][0]) if header_data['remarks'] and header_data['remarks'][0] else "",
            sheet_name=sheet_name
        )

        try:
            pq = header_data['plan_qty']
            if pq and pq[0]:
                header.plan_qty = float(pq[0][0])
        except:
            pass

        if header_data['plan_date'] and header_data['plan_date'][0]:
            header.plan_date = str(header_data['plan_date'][0][0])

        try:
            data = self._get_values(f"'{sheet_name}'!A16:Y")
        except:
            return BOM(header=header, combos=[])

        combos = []
        current_combo = None

        for row in data:
            if len(row) < 15:
                continue

            component = str(row[14]) if len(row) > 14 and row[14] else ""
            fabric_quality = str(row[10]) if len(row) > 10 and row[10] else ""
            color_id = str(row[7]) if len(row) > 7 and row[7] else ""

            if component.strip() == 'Planning Qnty':
                if current_combo:
                    combos.append(current_combo)

                current_combo = Combo(
                    combo_sr_no=int(row[3]) if len(row) > 3 and row[3] else 1,
                    combo_name=str(row[4]) if len(row) > 4 and row[4] else "",
                    lot_no=str(row[5]) if len(row) > 5 and row[5] else "",
                    lot_count=int(row[6]) if len(row) > 6 and row[6] else 1,
                    color_id=color_id,
                    color_code=str(row[8]) if len(row) > 8 and row[8] else "",
                    color_name=str(row[9]) if len(row) > 9 and row[9] else "",
                    plan_qty=float(row[17]) if len(row) > 17 and row[17] else 0,
                    bom_lines=[]
                )
            elif current_combo:
                has_fabric = fabric_quality.strip() != ''
                has_component = component.strip() != '' and component.strip() != 'Planning Qnty'

                if has_fabric or has_component:
                    current_combo.bom_lines.append(BOMLine(
                        fabric_quality=fabric_quality.strip() if has_fabric else "",
                        plan_rat_gsm=str(row[12]) if len(row) > 12 and row[12] else "",
                        priority=str(row[13]) if len(row) > 13 and row[13] else "",
                        component=component.strip() if has_component else "",
                        avg=float(row[15]) if len(row) > 15 and row[15] else 0,
                        unit=str(row[16]) if len(row) > 16 and row[16] else "",
                        extra_pcs=float(row[18]) if len(row) > 18 and row[18] else 0,
                        wastage_pcs=float(row[19]) if len(row) > 19 and row[19] else 0,
                        ready_fabric_need=float(row[20]) if len(row) > 20 and row[20] else 0,
                        shortage=float(row[21]) if len(row) > 21 and row[21] else 0,
                        greige_fabric_need=float(row[22]) if len(row) > 22 and row[22] else 0,
                        fc_no=str(row[11]) if len(row) > 11 and row[11] else ""
                    ))

        if current_combo:
            combos.append(current_combo)

        return BOM(header=header, combos=combos)

    def create_new_article_sheet(self, art_no: str) -> Dict[str, Any]:
        """Create a new article sheet from DUMMY template."""
        if self.demo_mode:
            return {"success": True, "sheet_name": art_no, "demo": True}

        if self._sheet_exists(art_no):
            return {"error": f"Sheet '{art_no}' already exists!"}

        if not self._sheet_exists('DUMMY'):
            return {"error": "DUMMY template not found!"}

        self._copy_sheet('DUMMY', art_no)
        self._update_values(f"'{art_no}'!P2", [[art_no]])

        return {"success": True, "sheet_name": art_no}

    # ============ BOM DATABASE FUNCTIONS ============

    def ensure_db_sheets(self):
        """Create BOM_INDEX, BOM_DATA, DPLAN_INDEX if they don't exist."""
        if self.demo_mode:
            return

        schemas = {
            'BOM_INDEX': [
                'BOM_UID', 'ART_NO', 'SET_NO', 'SEASON', 'BUYER', 'PLAN_DATE', 'PLAN_QTY',
                'REMARKS', 'COMBO_COUNT', 'LINE_COUNT', 'STATUS', 'DPLAN_NO', 'SHEET_NAME',
                'CREATED_AT', 'UPDATED_AT', 'CREATED_BY'
            ],
            'BOM_DATA': [
                'BOM_UID', 'ROW_TYPE', 'COMBO_SR_NO', 'COMBO_NAME', 'LOT_NO', 'LOT_COUNT',
                'COLOR_ID', 'COLOR_CODE', 'COLOR_NAME', 'PLAN_QTY',
                'FABRIC_QUALITY', 'FC_NO', 'PLAN_RAT_GSM', 'PRIORITY', 'COMPONENT', 'AVG', 'UNIT',
                'EXTRA_PCT', 'WASTAGE_PCT', 'SHORTAGE_PCT',
                'READY_FABRIC_NEED', 'GREIGE_FABRIC_NEED', 'NO_OF_ROLLS',
                'GREIGE_IS_MANUAL', 'LINE_ORDER'
            ],
            'DPLAN_INDEX': [
                'DPLAN_NO', 'BOM_COUNT', 'TOTAL_QTY', 'CREATED_AT', 'CREATED_BY', 'NOTES'
            ]
        }

        for name, headers in schemas.items():
            if not self._sheet_exists(name):
                self._create_sheet(name)
                self._update_values(f"'{name}'!A1", [headers])

    def generate_bom_uid(self) -> str:
        """Generate a unique BOM ID: BOM-YYYYMMDD-NNN."""
        now = datetime.now()
        date_str = now.strftime('%Y%m%d')
        prefix = f'BOM-{date_str}-'

        if self.demo_mode:
            return f"{prefix}001"

        try:
            data = self._get_values("'BOM_INDEX'!A:A")
            max_seq = 0
            for row in data[1:]:
                if row and str(row[0]).startswith(prefix):
                    try:
                        seq = int(str(row[0])[len(prefix):])
                        if seq > max_seq:
                            max_seq = seq
                    except:
                        pass
            return f"{prefix}{str(max_seq + 1).zfill(3)}"
        except:
            return f"{prefix}001"

    def save_bom_full(self, uid: Optional[str], header: BOMHeader, combos: List[Combo]) -> Dict[str, Any]:
        """Save BOM to database sheets and article tab."""
        if self.demo_mode:
            new_uid = uid or self.generate_bom_uid()
            return {
                "success": True,
                "uid": new_uid,
                "message": f"BOM {new_uid} saved (DEMO MODE - not actually saved)",
                "demo": True
            }

        self.ensure_db_sheets()

        is_edit = uid is not None
        if not is_edit:
            uid = self.generate_bom_uid()

        now = datetime.now().isoformat()
        user = "webapp_user"

        total_lines = sum(len(c.bom_lines) for c in combos)

        index_row = [
            uid,
            header.art_no or "",
            header.set_no or "",
            header.season or "",
            header.buyer or "",
            header.plan_date or "",
            header.plan_qty or 0,
            header.remarks or "",
            len(combos),
            total_lines,
            'UNALLOCATED',
            '',
            header.art_no or uid,
            now if not is_edit else "",
            now,
            user if not is_edit else ""
        ]

        if is_edit:
            data = self._get_values("'BOM_INDEX'!A:A")
            for i, row in enumerate(data):
                if row and str(row[0]) == uid:
                    self._update_values(f"'BOM_INDEX'!A{i+1}:P{i+1}", [index_row])
                    break
        else:
            self._append_values("'BOM_INDEX'!A:P", [index_row])

        new_rows = []
        line_order = 0

        for c_idx, combo in enumerate(combos):
            line_order += 1

            new_rows.append([
                uid, 'PLANNING',
                combo.combo_sr_no or (c_idx + 1),
                combo.combo_name or "",
                combo.lot_no or "",
                combo.lot_count or 1,
                combo.color_id or "",
                combo.color_code or "",
                combo.color_name or "",
                combo.plan_qty or 0,
                '', '', '', '', 'Planning Qnty', '', '',
                '', '', '',
                '', '', '',
                False, line_order
            ])

            for line in combo.bom_lines:
                line_order += 1
                extra_pct = line.extra_pcs or 0
                waste_pct = line.wastage_pcs or 0
                short_pct = line.shortage or 0
                avg_val = line.avg or 0
                order_qty = combo.plan_qty or 0

                ready_need = (order_qty + order_qty * extra_pct + order_qty * waste_pct) * avg_val
                is_manual_greige = line.unit == 'Pcs' and line.greige_fabric_need
                greige_need = line.greige_fabric_need if is_manual_greige else ready_need * (1 + short_pct)
                rolls = greige_need / 25 if line.unit == 'kg' else ""

                new_rows.append([
                    uid, 'BOM_LINE',
                    combo.combo_sr_no or (c_idx + 1),
                    combo.combo_name or "",
                    combo.lot_no or "",
                    combo.lot_count or 1,
                    combo.color_id or "",
                    combo.color_code or "",
                    combo.color_name or "",
                    '',
                    line.fabric_quality or "",
                    line.fc_no or "",
                    line.plan_rat_gsm or "",
                    line.priority or "",
                    line.component or "",
                    avg_val,
                    line.unit or "",
                    extra_pct,
                    waste_pct,
                    short_pct,
                    ready_need,
                    greige_need,
                    rolls,
                    is_manual_greige,
                    line_order
                ])

        if new_rows:
            self._append_values("'BOM_DATA'!A:Y", new_rows)

        tab_result = None
        try:
            sheet_name = header.art_no or uid
            self.save_bom_to_tab(sheet_name, header, combos)
            tab_result = {"success": True}
        except Exception as e:
            tab_result = {"success": False, "message": str(e)}

        return {
            "success": True,
            "uid": uid,
            "message": f"BOM {uid} saved to DB" + (" + tab" if tab_result and tab_result.get("success") else ""),
            "tab_result": tab_result
        }

    def save_bom_to_tab(self, sheet_name: str, header: BOMHeader, combos: List[Combo]):
        """Save BOM data to article sheet tab."""
        if self.demo_mode:
            return

        if not self._sheet_exists(sheet_name):
            if self._sheet_exists('DUMMY'):
                self._copy_sheet('DUMMY', sheet_name)
            else:
                self._create_sheet(sheet_name)

        if header.art_no:
            self._update_values(f"'{sheet_name}'!P2", [[header.art_no]])
        if header.plan_date:
            self._update_values(f"'{sheet_name}'!T1", [[header.plan_date]])
        if header.remarks:
            self._update_values(f"'{sheet_name}'!O5", [[header.remarks]])

        try:
            self._clear_range(f"'{sheet_name}'!A16:Y1000")
        except:
            pass

        set_no = header.set_no or ""
        buyer = header.buyer or ""
        art_no = header.art_no or ""

        rows = []
        for combo in combos:
            rows.append([
                set_no, buyer, art_no, combo.combo_sr_no, combo.combo_name,
                combo.lot_no, combo.lot_count or 1, combo.color_id,
                combo.color_code, combo.color_name, '', '', '', '',
                'Planning Qnty', '', '', combo.plan_qty, '', '', '', '', '', '', ''
            ])

            for line in combo.bom_lines:
                rows.append([
                    set_no, buyer, art_no, combo.combo_sr_no, combo.combo_name,
                    combo.lot_no, combo.lot_count or 1, combo.color_id,
                    combo.color_code, combo.color_name,
                    line.fabric_quality, line.fc_no or '', line.plan_rat_gsm, line.priority,
                    line.component, line.avg, line.unit,
                    '',
                    line.extra_pcs if line.extra_pcs else '',
                    line.wastage_pcs if line.wastage_pcs else '',
                    '', '', '', '', ''
                ])

            rows.append([''] * 25)

        if rows:
            self._update_values(f"'{sheet_name}'!A16:Y{15 + len(rows)}", rows)

    def load_bom_by_uid(self, uid: str) -> BOM:
        """Load full BOM from database by UID."""
        if self.demo_mode:
            return self._get_demo_bom("DEMO-" + uid)

        self.ensure_db_sheets()

        index_data = self._get_values("'BOM_INDEX'!A:P")
        header = None

        for row in index_data[1:]:
            if row and str(row[0]) == uid:
                header = BOMHeader(
                    uid=str(row[0]),
                    art_no=str(row[1]) if len(row) > 1 else "",
                    set_no=str(row[2]) if len(row) > 2 else "",
                    season=str(row[3]) if len(row) > 3 else "",
                    buyer=str(row[4]) if len(row) > 4 else "",
                    plan_date=str(row[5]) if len(row) > 5 else "",
                    plan_qty=float(row[6]) if len(row) > 6 and row[6] else 0,
                    remarks=str(row[7]) if len(row) > 7 else "",
                    combo_count=int(row[8]) if len(row) > 8 and row[8] else 0,
                    line_count=int(row[9]) if len(row) > 9 and row[9] else 0,
                    status=str(row[10]) if len(row) > 10 else "UNALLOCATED",
                    dplan_no=str(row[11]) if len(row) > 11 else "",
                    sheet_name=str(row[12]) if len(row) > 12 else "",
                    created_at=str(row[13]) if len(row) > 13 else "",
                    updated_at=str(row[14]) if len(row) > 14 else "",
                    created_by=str(row[15]) if len(row) > 15 else ""
                )
                break

        if not header:
            raise Exception(f"BOM not found: {uid}")

        data = self._get_values("'BOM_DATA'!A:Y")
        combos = []
        current_combo = None

        for row in data[1:]:
            if not row or str(row[0]) != uid:
                continue

            if str(row[1]) == 'PLANNING':
                if current_combo:
                    combos.append(current_combo)
                current_combo = Combo(
                    combo_sr_no=int(row[2]) if len(row) > 2 and row[2] else 1,
                    combo_name=str(row[3]) if len(row) > 3 else "",
                    lot_no=str(row[4]) if len(row) > 4 else "",
                    lot_count=int(row[5]) if len(row) > 5 and row[5] else 1,
                    color_id=str(row[6]) if len(row) > 6 else "",
                    color_code=str(row[7]) if len(row) > 7 else "",
                    color_name=str(row[8]) if len(row) > 8 else "",
                    plan_qty=float(row[9]) if len(row) > 9 and row[9] else 0,
                    bom_lines=[]
                )
            elif str(row[1]) == 'BOM_LINE' and current_combo:
                current_combo.bom_lines.append(BOMLine(
                    fabric_quality=str(row[10]) if len(row) > 10 else "",
                    fc_no=str(row[11]) if len(row) > 11 else "",
                    plan_rat_gsm=str(row[12]) if len(row) > 12 else "",
                    priority=str(row[13]) if len(row) > 13 else "",
                    component=str(row[14]) if len(row) > 14 else "",
                    avg=float(row[15]) if len(row) > 15 and row[15] else 0,
                    unit=str(row[16]) if len(row) > 16 else "",
                    extra_pcs=float(row[17]) if len(row) > 17 and row[17] else 0,
                    wastage_pcs=float(row[18]) if len(row) > 18 and row[18] else 0,
                    shortage=float(row[19]) if len(row) > 19 and row[19] else 0,
                    ready_fabric_need=float(row[20]) if len(row) > 20 and row[20] else 0,
                    greige_fabric_need=float(row[21]) if len(row) > 21 and row[21] else 0,
                    no_of_rolls=float(row[22]) if len(row) > 22 and row[22] else None,
                    greige_is_manual=bool(row[23]) if len(row) > 23 else False
                ))

        if current_combo:
            combos.append(current_combo)

        return BOM(header=header, combos=combos)

    def load_bom_index(self, status: Optional[str] = None, dplan_no: Optional[str] = None) -> List[BOMIndexItem]:
        """Load BOM index with optional filtering."""
        if self.demo_mode:
            demo_items = [
                BOMIndexItem(
                    uid="BOM-20250215-001",
                    art_no="1307 HI",
                    set_no="2609",
                    season="SUMMER-2025",
                    buyer="DEMO BUYER",
                    plan_qty=5000,
                    combo_count=2,
                    line_count=2,
                    status="UNALLOCATED",
                    created_at=datetime.now().isoformat()
                ),
                BOMIndexItem(
                    uid="BOM-20250215-002",
                    art_no="1405 PQ",
                    set_no="2610",
                    season="SUMMER-2025",
                    buyer="DEMO BUYER",
                    plan_qty=3000,
                    combo_count=1,
                    line_count=1,
                    status="UNALLOCATED",
                    created_at=datetime.now().isoformat()
                ),
            ]
            if status:
                demo_items = [i for i in demo_items if i.status == status]
            return demo_items

        self.ensure_db_sheets()

        try:
            data = self._get_values("'BOM_INDEX'!A:P")
        except:
            return []

        results = []
        for row in data[1:]:
            if not row:
                continue

            row_status = str(row[10]) if len(row) > 10 else ""
            row_dplan = str(row[11]) if len(row) > 11 else ""

            if status and row_status != status:
                continue
            if dplan_no and row_dplan != dplan_no:
                continue

            results.append(BOMIndexItem(
                uid=str(row[0]) if row else "",
                art_no=str(row[1]) if len(row) > 1 else "",
                set_no=str(row[2]) if len(row) > 2 else "",
                season=str(row[3]) if len(row) > 3 else "",
                buyer=str(row[4]) if len(row) > 4 else "",
                plan_date=str(row[5]) if len(row) > 5 else "",
                plan_qty=float(row[6]) if len(row) > 6 and row[6] else 0,
                remarks=str(row[7]) if len(row) > 7 else "",
                combo_count=int(row[8]) if len(row) > 8 and row[8] else 0,
                line_count=int(row[9]) if len(row) > 9 and row[9] else 0,
                status=row_status,
                dplan_no=row_dplan,
                sheet_name=str(row[12]) if len(row) > 12 else "",
                created_at=str(row[13]) if len(row) > 13 else "",
                updated_at=str(row[14]) if len(row) > 14 else "",
                created_by=str(row[15]) if len(row) > 15 else ""
            ))

        return results

    def allocate_boms(self, uids: List[str], dplan_no: str) -> Dict[str, Any]:
        """Assign BOMs to a Dyeing Plan."""
        if self.demo_mode:
            return {
                "success": True,
                "allocated": len(uids),
                "dplan_no": dplan_no,
                "message": f"{len(uids)} BOMs allocated to {dplan_no} (DEMO MODE)"
            }

        self.ensure_db_sheets()

        now = datetime.now().isoformat()
        user = "webapp_user"

        data = self._get_values("'BOM_INDEX'!A:P")
        allocated = 0
        total_qty = 0

        for i, row in enumerate(data[1:], start=2):
            if row and str(row[0]) in uids:
                self._update_values(f"'BOM_INDEX'!K{i}", [['ALLOCATED']])
                self._update_values(f"'BOM_INDEX'!L{i}", [[dplan_no]])
                self._update_values(f"'BOM_INDEX'!O{i}", [[now]])
                allocated += 1
                total_qty += float(row[6]) if len(row) > 6 and row[6] else 0

        dplan_data = self._get_values("'DPLAN_INDEX'!A:A")
        dplan_exists = False

        for i, row in enumerate(dplan_data[1:], start=2):
            if row and str(row[0]) == dplan_no:
                self._update_values(f"'DPLAN_INDEX'!B{i}:C{i}", [[allocated, total_qty]])
                dplan_exists = True
                break

        if not dplan_exists:
            self._append_values("'DPLAN_INDEX'!A:F", [[dplan_no, allocated, total_qty, now, user, '']])

        return {
            "success": True,
            "allocated": allocated,
            "dplan_no": dplan_no,
            "message": f"{allocated} BOMs allocated to {dplan_no}"
        }

    def unallocate_boms(self, uids: List[str]) -> Dict[str, Any]:
        """Move BOMs back to UNALLOCATED status."""
        if self.demo_mode:
            return {"success": True, "unallocated": len(uids)}

        self.ensure_db_sheets()

        now = datetime.now().isoformat()
        data = self._get_values("'BOM_INDEX'!A:P")
        unallocated = 0

        for i, row in enumerate(data[1:], start=2):
            if row and str(row[0]) in uids:
                self._update_values(f"'BOM_INDEX'!K{i}", [['UNALLOCATED']])
                self._update_values(f"'BOM_INDEX'!L{i}", [['']])
                self._update_values(f"'BOM_INDEX'!O{i}", [[now]])
                unallocated += 1

        return {"success": True, "unallocated": unallocated}

    def load_dplans(self) -> List[DyeingPlan]:
        """Load all Dyeing Plans."""
        if self.demo_mode:
            return [
                DyeingPlan(
                    dplan_no="2609 DP",
                    bom_count=2,
                    total_qty=8000,
                    created_at=datetime.now().isoformat(),
                    created_by="demo_user"
                )
            ]

        self.ensure_db_sheets()

        try:
            data = self._get_values("'DPLAN_INDEX'!A:F")
        except:
            return []

        plans = []
        for row in data[1:]:
            if not row:
                continue
            plans.append(DyeingPlan(
                dplan_no=str(row[0]) if row else "",
                bom_count=int(row[1]) if len(row) > 1 and row[1] else 0,
                total_qty=float(row[2]) if len(row) > 2 and row[2] else 0,
                created_at=str(row[3]) if len(row) > 3 else "",
                created_by=str(row[4]) if len(row) > 4 else "",
                notes=str(row[5]) if len(row) > 5 else ""
            ))

        return plans

    def auto_import_all_boms(self) -> Dict[str, Any]:
        """Auto-import all existing article BOMs into the DB."""
        if self.demo_mode:
            return {
                "imported": 0,
                "skipped": 3,
                "errors": 0,
                "items": self.load_bom_index(status='UNALLOCATED')
            }

        self.ensure_db_sheets()

        articles = self.get_article_list()

        existing_arts = set()
        try:
            idx_data = self._get_values("'BOM_INDEX'!B:B")
            for row in idx_data[1:]:
                if row and str(row[0]).strip():
                    existing_arts.add(str(row[0]).strip())
        except:
            pass

        imported = 0
        skipped = 0
        errors = 0

        for art in articles:
            art_no = art.art_no.strip()
            if art_no in existing_arts:
                skipped += 1
                continue

            try:
                bom = self.load_article_bom(art.sheet_name)
                if not bom.combos:
                    skipped += 1
                    continue

                header = bom.header
                if not header.art_no:
                    header.art_no = art_no

                self.save_bom_full(None, header, bom.combos)
                imported += 1
                existing_arts.add(art_no)
            except Exception as e:
                errors += 1

        pool = self.load_bom_index(status='UNALLOCATED')
        return {
            "imported": imported,
            "skipped": skipped,
            "errors": errors,
            "items": pool
        }


# Singleton instance
_sheets_service = None


def get_sheets_service() -> SheetsService:
    """Get singleton sheets service instance."""
    global _sheets_service
    if _sheets_service is None:
        _sheets_service = SheetsService()
    return _sheets_service
