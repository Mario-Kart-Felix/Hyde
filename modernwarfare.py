import logging
from glob import glob
from typing import Any, Dict, List, Optional, Union

from util import Utility

log: logging.Logger = logging.getLogger(__name__)


class ModernWarfare:
    """
    Call of Duty: Modern Warfare (2019)
    
    Supported XAssets:
    - Accessories
    - Battle Pass Items
    - Bundles
    - Calling Cards
    - Camos
    - Charms
    - Consumables
    - Emblems
    - Finishing Moves
    - Features
    - Officer Challenges
    - Operator Quips
    - Operator Skins
    - Special Items
    - Sprays
    - Stickers
    - Vehicle Camos
    - Weapons
    - Weapon Unlock Challenges
    - Weekly Warzone Challenges
    - Weekly Multiplayer Challenges
    """

    def __init__(self: Any):
        # Types
        self.csv = Optional[List[List[str]]]
        self.csvRow = Optional[List[str]]
        self.csvColumn = Optional[Union[str, int]]
        self.json = Optional[Dict[str, str]]

        # Global / Reused XAssets
        self.localize: self.json = Utility.ReadFile(
            self, "import/Modern Warfare/", "localize", "json"
        )
        self.lootMaster: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "loot_master", "csv"
        )

    def GetLootType(self: Any, value: int) -> Optional[str]:
        """
        Return the loot type for the given XAsset ID.

        Requires loot_master.csv
        """

        # Skip the first row of loot_master.csv
        for row in self.lootMaster[1:]:
            if (value >= Utility.GetColumn(self, row[0])) and (
                value <= Utility.GetColumn(self, row[1])
            ):
                return ModernWarfare.GetLocalize(self, row[5])

    def GetLootRarity(self: Any, value: int) -> Optional[str]:
        """
        Return the loot rarity for the given value.
        
        Requires localize.json
        """

        return ModernWarfare.GetLocalize(self, f"LOOT_MP/QUALITY_{value}")

    def GetLootSeason(self: Any, value: int) -> Optional[str]:
        """
        Return the loot season for the given value.

        Requires localize.json
        """

        if value == 0:
            # No Season information display, does not necessarily mean
            # that the item is a part of Season 0.
            return
        elif (value % 1000) != 0:
            # Loot Season values are multiples of 1,000, this will return
            # null for unknown values.
            return

        # TODO: Return icon for Loot Season, maybe take advantage of seasons.csv?
        # Example: icon_season_s02

        return ModernWarfare.GetLocalize(self, f"SEASONS/SEASON_{round(value / 1000)}")

    def GetLocalize(self: Any, key: str) -> Optional[str]:
        """
        Return the localized string for the requested key.
        
        Requires localize.json
        """

        value: Optional[str] = self.localize.get(key)

        starts: List[str] = [
            "ST CARD ",
            "ST_CARD_",
            "CARD ",
            "EMBLEM 6",
            "EMBLEM 7",
            "EMBLEM_",
            "STICKER ",
            "STICKER_",
            "STICKER NAME",
            "( Temporary - ",
            "COS_",
            "QUIP_",
            "OPERATOR_",
            "SPRAY ",
            "SPRAY_",
            "AR_",
            "SM_",
            "SN_",
            "SH_",
            "PI_",
            "LA_",
            "ME_",
            "LM_",
            "BP_",
        ]
        ends: List[str] = [" Flavor Text...", "_DESC", " NAME MISSING"]

        if value is None:
            return None
        elif value == "":
            return None
        else:
            # TODO: Find a better way to return null on placeholder values.
            for placeholder in starts:
                if value.lower().startswith(placeholder.lower()):
                    return None

            for placeholder in ends:
                if value.lower().endswith(placeholder.lower()):
                    return None

            return Utility.StripColors(self, value)

    def CompileAccessories(self: Any) -> None:
        """
        Compile the Accessory XAssets.
        
        Requires accessory_ids.csv and accessorytable.csv
        """

        ids: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "accessory_ids", "csv"
        )
        table: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "accessorytable", "csv"
        )

        if (ids is None) or (table is None):
            return

        accessories: List[dict] = []

        # Skip the first row of accessory_ids.csv and accessorytable.csv
        for idRow, tableRow in zip(ids[1:], table[1:]):
            idColumn: self.csvColumn = Utility.GetColumn(self, idRow[1])
            tableColumn: self.csvColumn = Utility.GetColumn(self, tableRow[0])

            if idColumn != tableColumn:
                tableRow: self.csvRow = Utility.GetRow(self, str(idColumn), table, 0)

                if tableRow is None:
                    log.warning(
                        f"Mismatch in accessory_ids.csv, {idColumn} does not exist in accessorytable.csv ({tableColumn})"
                    )

                    continue

            accessories.append(
                {
                    "id": Utility.GetColumn(self, idRow[0]),
                    "name": ModernWarfare.GetLocalize(self, tableRow[4]),
                    "description": ModernWarfare.GetLocalize(self, tableRow[5]),
                    "flavor": ModernWarfare.GetLocalize(
                        self, f"STORE_FLAVOR/{idRow[1].upper()}_FLAVOR"
                    ),
                    "type": ModernWarfare.GetLootType(self, int(idRow[0])),
                    "rarity": ModernWarfare.GetLootRarity(self, int(idRow[2])),
                    "season": ModernWarfare.GetLootSeason(self, int(idRow[5])),
                    "image": Utility.GetColumn(self, tableRow[14]),
                }
            )

        status: bool = Utility.WriteFile(
            self, "export/Modern Warfare/", "accessories", "json", accessories
        )

        if status is True:
            log.info(f"Compiled {len(accessories):,} Accessories")

    def CompileBattlePassItems(self: Any) -> None:
        """
        Compile the Battle Pass Item XAssets.

        Requires battlepass_ids.csv
        """

        ids: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "battlepass_ids", "csv"
        )

        if ids is None:
            return

        items: List[dict] = []

        for idRow in ids:
            items.append(
                {
                    "id": Utility.GetColumn(self, idRow[0]),
                    "name": ModernWarfare.GetLocalize(self, idRow[18]),
                    "type": ModernWarfare.GetLootType(self, int(idRow[0])),
                    "rarity": ModernWarfare.GetLootRarity(self, int(idRow[3])),
                    "image": "battlepass_emblem",
                    "background": "ui_loot_bg_battlepass",
                }
            )

        status: bool = Utility.WriteFile(
            self, "export/Modern Warfare/", "battlePassItems", "json", items
        )

        if status is True:
            log.info(f"Compiled {len(items):,} Battle Pass Items")

    def CompileBundles(self: Any) -> None:
        """
        Compile the Bundle XAssets.
        
        Requires bundle_ids.csv
        """

        ids: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "bundle_ids", "csv"
        )

        if ids is None:
            return

        bundles: List[dict] = []

        for idRow in ids:
            items: List[dict] = []

            # Bundles contain a maximum of 10 items. The IDs for these
            # items are located between columns 14 and 24.
            for i in range(14, 24):
                if (itemId := Utility.GetColumn(self, idRow[i])) is not None:
                    items.append(
                        {
                            "id": itemId,
                            "type": ModernWarfare.GetLootType(self, int(idRow[i])),
                        }
                    )

            bundles.append(
                {
                    "id": Utility.GetColumn(self, idRow[0]),
                    "name": ModernWarfare.GetLocalize(self, idRow[1]),
                    "description": ModernWarfare.GetLocalize(self, idRow[2]),
                    "flavor": ModernWarfare.GetLocalize(self, idRow[3]),
                    "type": ModernWarfare.GetLocalize(self, idRow[5]),
                    "season": ModernWarfare.GetLootSeason(self, int(idRow[4])),
                    "billboard": Utility.GetColumn(self, idRow[6]),
                    "logo": Utility.GetColumn(self, idRow[8]),
                    "price": Utility.GetColumn(self, idRow[10]),
                    "items": items,
                }
            )

        status: bool = Utility.WriteFile(
            self, "export/Modern Warfare/", "bundles", "json", bundles
        )

        if status is True:
            log.info(f"Compiled {len(bundles):,} Bundles")

    def CompileCallingCards(self: Any) -> None:
        """
        Compile the Calling Card XAssets.
        
        Requires playercards_ids.csv and callingcards.csv
        """

        ids: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "playercards_ids", "csv"
        )
        table: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "callingcards", "csv"
        )

        if (ids is None) or (table is None):
            return

        cards: List[dict] = []

        # Skip the first row of callingcards.csv
        for idRow, tableRow in zip(ids, table[1:]):
            idColumn: self.csvColumn = Utility.GetColumn(self, idRow[1])
            tableColumn: self.csvColumn = Utility.GetColumn(self, tableRow[1])

            if idColumn != tableColumn:
                tableRow: self.csvRow = Utility.GetRow(self, str(idColumn), table, 1)

                if tableRow is None:
                    log.warning(
                        f"Mismatch in playercards_ids.csv, {idColumn} does not exist in callingcards.csv ({tableColumn})"
                    )

                    continue

            cards.append(
                {
                    "id": Utility.GetColumn(self, idRow[0]),
                    "name": ModernWarfare.GetLocalize(self, tableRow[3]),
                    "type": ModernWarfare.GetLootType(self, int(idRow[0])),
                    "rarity": ModernWarfare.GetLootRarity(self, int(idRow[2])),
                    "season": ModernWarfare.GetLootSeason(self, int(idRow[5])),
                    "image": Utility.GetColumn(self, idRow[1]),
                }
            )

        status: bool = Utility.WriteFile(
            self, "export/Modern Warfare/", "callingCards", "json", cards
        )

        if status is True:
            log.info(f"Compiled {len(cards):,} Calling Cards")

    def CompileCamos(self: Any) -> None:
        """
        Compile the Camo XAssets.
        
        Requires camo_ids.csv and camotable.csv
        """

        ids: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "camo_ids", "csv"
        )
        table: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "camotable", "csv"
        )

        if (ids is None) or (table is None):
            return

        camos: List[dict] = []

        # Skip the first row of camotable.csv
        for idRow, tableRow in zip(ids, table[1:]):
            idColumn: self.csvColumn = Utility.GetColumn(self, idRow[1])
            tableColumn: self.csvColumn = Utility.GetColumn(self, tableRow[1])

            if idColumn != tableColumn:
                tableRow: self.csvRow = Utility.GetRow(self, str(idColumn), table, 1)

                if tableRow is None:
                    log.warning(
                        f"Mismatch in camo_ids.csv, {idColumn} does not exist in camotable.csv ({tableColumn})"
                    )

                    continue

            camos.append(
                {
                    "id": Utility.GetColumn(self, idRow[0]),
                    "name": ModernWarfare.GetLocalize(self, tableRow[7]),
                    "category": Utility.GetColumn(self, tableRow[3]),
                    "type": ModernWarfare.GetLootType(self, int(idRow[0])),
                    "rarity": ModernWarfare.GetLootRarity(self, int(idRow[2])),
                    "season": ModernWarfare.GetLootSeason(self, int(idRow[5])),
                    "unlock": Utility.GetColumn(self, tableRow[4]),
                    "image": Utility.GetColumn(self, tableRow[8]),
                }
            )

        # TODO: Find a better way to determine this data.
        for camo in camos:
            if isinstance((val := camo.get("category")), str):
                camo["category"] = val.capitalize()

            if isinstance((val := camo.get("unlock")), str):
                camo["unlock"] = val.capitalize()

        status: bool = Utility.WriteFile(
            self, "export/Modern Warfare/", "camos", "json", camos
        )

        if status is True:
            log.info(f"Compiled {len(camos):,} Camos")

    def CompileCharms(self: Any) -> None:
        """
        Compile the Charm XAssets.
        
        Requires weapon_charm_ids.csv and weaponcharmtable.csv
        """

        ids: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "weapon_charm_ids", "csv"
        )
        table: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "weaponcharmtable", "csv"
        )

        if (ids is None) or (table is None):
            return

        charms: List[dict] = []

        # Skip the first row of weaponcharmtable.csv
        for idRow, tableRow in zip(ids, table[1:]):
            idColumn: self.csvColumn = Utility.GetColumn(self, idRow[1])
            tableColumn: self.csvColumn = Utility.GetColumn(self, tableRow[1])

            if idColumn != tableColumn:
                tableRow: self.csvRow = Utility.GetRow(self, str(idColumn), table, 1)

                if tableRow is None:
                    log.warning(
                        f"Mismatch in weapon_charm_ids.csv, {idColumn} does not exist in weaponcharmtable.csv ({tableColumn})"
                    )

                    continue

            charms.append(
                {
                    "id": Utility.GetColumn(self, idRow[0]),
                    "name": ModernWarfare.GetLocalize(self, tableRow[2]),
                    "flavor": ModernWarfare.GetLocalize(
                        self, f"STORE_FLAVOR/{idRow[1].upper()}_FLAVOR"
                    ),
                    "type": ModernWarfare.GetLootType(self, int(idRow[0])),
                    "rarity": ModernWarfare.GetLootRarity(self, int(idRow[2])),
                    "season": ModernWarfare.GetLootSeason(self, int(idRow[5])),
                    "image": Utility.GetColumn(self, tableRow[3]),
                    "background": "ui_loot_bg_charm",
                }
            )

        status: bool = Utility.WriteFile(
            self, "export/Modern Warfare/", "charms", "json", charms
        )

        if status is True:
            log.info(f"Compiled {len(charms):,} Charms")

    def CompileConsumables(self: Any) -> None:
        """
        Compile the Consumable XAssets.

        Requires consumable_ids.csv
        """

        ids: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "consumable_ids", "csv"
        )

        if ids is None:
            return

        consumables: List[dict] = []

        for idRow in ids:
            consumables.append(
                {
                    "id": Utility.GetColumn(self, idRow[0]),
                    "name": ModernWarfare.GetLocalize(self, idRow[8]),
                    "description": ModernWarfare.GetLocalize(self, idRow[11]),
                    "type": ModernWarfare.GetLootType(self, int(idRow[0])),
                    "rarity": ModernWarfare.GetLootRarity(self, int(idRow[2])),
                    "image": Utility.GetColumn(self, idRow[9]),
                    "background": "ui_loot_bg_generic",
                }
            )

        status: bool = Utility.WriteFile(
            self, "export/Modern Warfare/", "consumables", "json", consumables
        )

        if status is True:
            log.info(f"Compiled {len(consumables):,} Consumables")

    def CompileEmblems(self: Any) -> None:
        """
        Compile the Emblem XAssets.
        
        Requires emblems_ids.csv and emblemtable.csv
        """

        ids: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "emblems_ids", "csv"
        )
        table: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "emblemtable", "csv"
        )

        if (ids is None) or (table is None):
            return

        emblems: List[dict] = []

        # Skip the first row of emblemtable.csv
        for idRow, tableRow in zip(ids, table[1:]):
            idColumn: self.csvColumn = Utility.GetColumn(self, idRow[1])
            tableColumn: self.csvColumn = Utility.GetColumn(self, tableRow[1])

            if idColumn != tableColumn:
                tableRow: self.csvRow = Utility.GetRow(self, str(idColumn), table, 1)

                if tableRow is None:
                    log.warning(
                        f"Mismatch in emblems_ids.csv, {idColumn} does not exist in emblemtable.csv ({tableColumn})"
                    )

                    continue

            emblems.append(
                {
                    "id": Utility.GetColumn(self, idRow[0]),
                    "name": ModernWarfare.GetLocalize(self, tableRow[3]),
                    "type": ModernWarfare.GetLootType(self, int(idRow[0])),
                    "rarity": ModernWarfare.GetLootRarity(self, int(idRow[2])),
                    "season": ModernWarfare.GetLootSeason(self, int(idRow[5])),
                    "image": Utility.GetColumn(self, tableRow[1]),
                    "background": "ui_loot_bg_emblem",
                }
            )

        status: bool = Utility.WriteFile(
            self, "export/Modern Warfare/", "emblems", "json", emblems
        )

        if status is True:
            log.info(f"Compiled {len(emblems):,} Emblems")

    def CompileExecutions(self: Any) -> None:
        """
        Compile the Finishing Move XAssets.
        
        Requires executions_ids.csv, executiontable.csv, and operators.csv
        """

        ids: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "executions_ids", "csv"
        )
        table: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "executiontable", "csv"
        )

        if (ids is None) or (table is None):
            return

        executions: List[dict] = []

        # Skip the first 3 rows of executiontable.csv
        for idRow, tableRow in zip(ids, table[3:]):
            idColumn: self.csvColumn = Utility.GetColumn(self, idRow[1])
            tableColumn: self.csvColumn = Utility.GetColumn(self, tableRow[1])

            if idColumn != tableColumn:
                tableRow: self.csvRow = Utility.GetRow(self, str(idColumn), table, 1)

                if tableRow is None:
                    # Log to debug because there are typically many missing executions.
                    log.debug(
                        f"Mismatch in executions_ids.csv, {idColumn} does not exist in executiontable.csv ({tableColumn})"
                    )

                    continue

            executions.append(
                {
                    "id": Utility.GetColumn(self, idRow[0]),
                    "name": ModernWarfare.GetLocalize(self, tableRow[3]),
                    "type": ModernWarfare.GetLootType(self, int(idRow[0])),
                    "rarity": ModernWarfare.GetLootRarity(self, int(idRow[2])),
                    "season": ModernWarfare.GetLootSeason(self, int(idRow[5])),
                    "operatorId": None,  # This is determined later
                    "operator": Utility.GetColumn(self, tableRow[2]),
                    "image": Utility.GetColumn(self, tableRow[17]),
                    "background": "ui_loot_bg_execution",
                    "video": Utility.GetColumn(self, tableRow[11]),
                }
            )

        # TODO: Find a better way to determine the Operator ID
        table: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "operators", "csv"
        )

        if table is not None:
            for execution in executions:
                if execution.get("operator") is None:
                    continue

                if execution.get("operator") == "universal_ref":
                    execution["operator"] = "Universal"

                    continue

                for tableRow in table:
                    if Utility.GetColumn(self, tableRow[1]) == execution.get(
                        "operator"
                    ):
                        execution["operatorId"] = Utility.GetColumn(self, tableRow[0])

                        if (
                            name := ModernWarfare.GetLocalize(self, tableRow[2])
                        ) is not None:
                            execution["operator"] = name.capitalize()

        status: bool = Utility.WriteFile(
            self, "export/Modern Warfare/", "executions", "json", executions
        )

        if status is True:
            log.info(f"Compiled {len(executions):,} Finishing Moves")

    def CompileFeatures(self: Any) -> None:
        """
        Compile the Feature XAssets.

        Requires feature_ids.csv
        """

        ids: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "feature_ids", "csv"
        )

        if ids is None:
            return

        features: List[dict] = []

        for idRow in ids:
            features.append(
                {
                    "id": Utility.GetColumn(self, idRow[0]),
                    "name": ModernWarfare.GetLocalize(self, idRow[6]),
                    "description": ModernWarfare.GetLocalize(self, idRow[7]),
                    "type": ModernWarfare.GetLootType(self, int(idRow[0])),
                    "rarity": ModernWarfare.GetLootRarity(self, int(idRow[2])),
                    "image": Utility.GetColumn(self, idRow[9]),
                    "background": "ui_loot_bg_generic",
                }
            )

        status: bool = Utility.WriteFile(
            self, "export/Modern Warfare/", "features", "json", features
        )

        if status is True:
            log.info(f"Compiled {len(features):,} Features")

    def CompileOfficerChallenges(self: Any) -> None:
        """
        Compile the Officer Challenge XAssets.

        Requires elder_challenges.csv
        """

        table: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "elder_challenges", "csv"
        )

        if table is None:
            return

        challenges: List[dict] = []

        for tableRow in table:
            # TODO: Find a better way to determine the Season number.
            tableColumn: self.csvColumn = Utility.GetColumn(self, tableRow[1])

            if (tableColumn is not None) and (
                str(tableColumn).startswith("ch_elder_s")
            ):
                col: Optional[Union[str, int]] = str(tableColumn).split("_")[2][1:]
                season: Optional[int] = int(col)
            else:
                season: Optional[int] = None

            challenges.append(
                {
                    "id": Utility.GetColumn(self, tableRow[0]),
                    "name": ModernWarfare.GetLocalize(self, tableRow[2]),
                    "description": ModernWarfare.GetLocalize(self, tableRow[3]).replace(
                        "&&1", tableRow[4]
                    ),
                    "amount": Utility.GetColumn(self, tableRow[4]),
                    "season": season,
                    "reward": Utility.GetColumn(self, tableRow[6]),
                }
            )

        status: bool = Utility.WriteFile(
            self, "export/Modern Warfare/", "officerChallenges", "json", challenges
        )

        if status is True:
            log.info(f"Compiled {len(challenges):,} Officer Challenges")

    def CompileQuips(self: Any) -> None:
        """
        Compile the Operator Quip XAssets.
        
        Requires operator_quip_ids.csv and operatorquips.csv
        """

        ids: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "operator_quip_ids", "csv"
        )
        table: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "operatorquips", "csv"
        )

        if (ids is None) or (table is None):
            return

        quips: List[dict] = []

        # Skip the first row of operatorquips.csv
        for idRow, tableRow in zip(ids, table[1:]):
            idColumn: self.csvColumn = Utility.GetColumn(self, idRow[1])
            tableColumn: self.csvColumn = Utility.GetColumn(self, tableRow[1])

            if idColumn != tableColumn:
                tableRow: self.csvRow = Utility.GetRow(self, str(idColumn), table, 1)

                if tableRow is None:
                    log.warning(
                        f"Mismatch in operator_quip_ids.csv, {idColumn} does not exist in operatorquips.csv ({tableColumn})"
                    )

                    continue

            quips.append(
                {
                    "id": Utility.GetColumn(self, idRow[0]),
                    "name": ModernWarfare.GetLocalize(self, tableRow[3]),
                    "description": ModernWarfare.GetLocalize(self, tableRow[8]),
                    "type": ModernWarfare.GetLootType(self, int(idRow[0])),
                    "rarity": ModernWarfare.GetLootRarity(self, int(idRow[2])),
                    "season": ModernWarfare.GetLootSeason(self, int(idRow[5])),
                    # TODO: Determine Operator ID.
                    "image": Utility.GetColumn(self, tableRow[4]),
                    "background": "ui_loot_bg_operator",
                }
            )

        status: bool = Utility.WriteFile(
            self, "export/Modern Warfare/", "quips", "json", quips
        )

        if status is True:
            log.info(f"Compiled {len(quips):,} Operator Quips")

    def CompileSkins(self: Any) -> None:
        """
        Compile the Operator Skin XAssets.
        
        Requires operator_skin_ids.csv, operatorskins.csv, and operators.csv
        """

        ids: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "operator_skin_ids", "csv"
        )
        table: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "operatorskins", "csv"
        )

        if (ids is None) or (table is None):
            return

        skins: List[dict] = []

        for idRow, tableRow in zip(ids, table):
            idColumn: self.csvColumn = Utility.GetColumn(self, idRow[1])
            tableColumn: self.csvColumn = Utility.GetColumn(self, tableRow[1])

            if idColumn != tableColumn:
                tableRow: self.csvRow = Utility.GetRow(self, str(idColumn), table, 1)

                if tableRow is None:
                    # Log to debug because there are typically many missing Operator Skins.
                    log.debug(
                        f"Mismatch in operator_skin_ids.csv, {idColumn} does not exist in operatorskins.csv ({tableColumn})"
                    )

                    continue

            skins.append(
                {
                    "id": Utility.GetColumn(self, idRow[0]),
                    "name": ModernWarfare.GetLocalize(self, tableRow[3]),
                    "description": ModernWarfare.GetLocalize(self, tableRow[15]),
                    "type": ModernWarfare.GetLootType(self, int(idRow[0])),
                    "rarity": ModernWarfare.GetLootRarity(self, int(idRow[2])),
                    "season": ModernWarfare.GetLootSeason(self, int(idRow[5])),
                    "operatorId": None,  # This is determined later
                    "operator": Utility.GetColumn(self, tableRow[2]),
                    "image": Utility.GetColumn(self, tableRow[18]),
                    "background": "ui_loot_bg_operator",
                }
            )

        # TODO: Find a better way to determine Operator ID.
        table: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "operators", "csv"
        )

        if table is not None:
            for skin in skins:
                if skin.get("operator") is None:
                    continue

                for tableRow in table:
                    if Utility.GetColumn(self, tableRow[1]) == skin.get("operator"):
                        skin["operatorId"] = Utility.GetColumn(self, tableRow[0])

                        if (
                            name := ModernWarfare.GetLocalize(self, tableRow[2])
                        ) is not None:
                            skin["operator"] = name.capitalize()

        status: bool = Utility.WriteFile(
            self, "export/Modern Warfare/", "skins", "json", skins
        )

        if status is True:
            log.info(f"Compiled {len(skins):,} Operator Skins")

    def CompileSpecialItems(self: Any) -> None:
        """
        Compile the Special Item XAssets.

        Requires special_ids.csv
        """

        ids: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "special_ids", "csv"
        )

        if ids is None:
            return

        items: List[dict] = []

        for idRow in ids:
            items.append(
                {
                    "id": Utility.GetColumn(self, idRow[0]),
                    "name": ModernWarfare.GetLocalize(self, idRow[2]),
                    "type": ModernWarfare.GetLootType(self, int(idRow[0])),
                    "rarity": ModernWarfare.GetLootRarity(self, idRow[4]),
                    "season": ModernWarfare.GetLootSeason(self, int(idRow[5])),
                    "image": Utility.GetColumn(self, idRow[3]),
                }
            )

        status: bool = Utility.WriteFile(
            self, "export/Modern Warfare/", "specialItems", "json", items
        )

        if status is True:
            log.info(f"Compiled {len(items):,} Special Items")

    def CompileSprays(self: Any) -> None:
        """
        Compile the Spray XAssets.
        
        Requires sprays_ids.csv and spraytable.csv
        """

        ids: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "sprays_ids", "csv"
        )
        table: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "spraytable", "csv"
        )

        if (ids is None) or (table is None):
            return

        sprays: List[dict] = []

        for idRow, tableRow in zip(ids, table):
            idColumn: self.csvColumn = Utility.GetColumn(self, idRow[1])
            tableColumn: self.csvColumn = Utility.GetColumn(self, tableRow[1])

            if idColumn != tableColumn:
                tableRow: self.csvRow = Utility.GetRow(self, str(idColumn), table, 1)

                if tableRow is None:
                    log.warning(
                        f"Mismatch in sprays_ids.csv, {idColumn} does not exist in spraytable.csv ({tableColumn})"
                    )

                    continue

            sprays.append(
                {
                    "id": Utility.GetColumn(self, idRow[0]),
                    "name": ModernWarfare.GetLocalize(self, tableRow[2]),
                    "type": ModernWarfare.GetLootType(self, int(idRow[0])),
                    "rarity": ModernWarfare.GetLootRarity(self, int(idRow[2])),
                    "season": ModernWarfare.GetLootSeason(self, int(idRow[5])),
                    "image": Utility.GetColumn(self, tableRow[3]),
                    "background": "ui_loot_bg_spray",
                }
            )

        status: bool = Utility.WriteFile(
            self, "export/Modern Warfare/", "sprays", "json", sprays
        )

        if status is True:
            log.info(f"Compiled {len(sprays):,} Sprays")

    def CompileStickers(self: Any) -> None:
        """
        Compile the Sticker XAssets.
        
        Requires sticker_ids.csv and weaponstickertable.csv
        """

        ids: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "sticker_ids", "csv"
        )
        table: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "weaponstickertable", "csv"
        )

        if (ids is None) or (table is None):
            return

        stickers: List[dict] = []

        # Skip the first 5 rows of weaponstickertable.csv
        for idRow, tableRow in zip(ids, table[5:]):
            idColumn: self.csvColumn = Utility.GetColumn(self, idRow[1])
            tableColumn: self.csvColumn = Utility.GetColumn(self, tableRow[1])

            if idColumn != tableColumn:
                tableRow: self.csvRow = Utility.GetRow(self, str(idColumn), table, 1)

                if tableRow is None:
                    log.warning(
                        f"Mismatch in sticker_ids.csv, {idColumn} does not exist in weaponstickertable.csv ({tableColumn})"
                    )

                    continue

            stickers.append(
                {
                    "id": Utility.GetColumn(self, idRow[0]),
                    "name": ModernWarfare.GetLocalize(self, tableRow[3]),
                    "type": ModernWarfare.GetLootType(self, int(idRow[0])),
                    "rarity": ModernWarfare.GetLootRarity(self, int(idRow[2])),
                    "season": ModernWarfare.GetLootSeason(self, int(idRow[5])),
                    "image": Utility.GetColumn(self, tableRow[4]),
                    "background": "ui_loot_bg_sticker",
                }
            )

        status: bool = Utility.WriteFile(
            self, "export/Modern Warfare/", "stickers", "json", stickers
        )

        if status is True:
            log.info(f"Compiled {len(stickers):,} Stickers")

    def CompileVehicleCamos(self: Any) -> None:
        """
        Compile the Vehicle Camo XAssets.
        
        Requires vehicle_camo_ids.csv and vehiclecamos.csv
        """

        ids: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "vehicle_camo_ids", "csv"
        )
        vehCamoTable: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "vehiclecamos", "csv"
        )

        if (ids is None) or (vehCamoTable is None):
            return

        vehCamos: List[dict] = []

        # Skip the first row of vehiclecamos.csv
        for idRow, tableRow in zip(ids, vehCamoTable[1:]):
            idColumn: self.csvColumn = Utility.GetColumn(self, idRow[0])
            tableColumn: self.csvColumn = Utility.GetColumn(self, tableRow[6])

            if idColumn != tableColumn:
                tableRow: self.csvRow = Utility.GetRow(
                    self, str(idColumn), vehCamoTable, 1
                )

                if tableRow is None:
                    log.warning(
                        f"Mismatch in vehicle_camo_ids.csv, {idColumn} does not exist in vehiclecamos.csv ({tableColumn})"
                    )

                    continue

            vehCamos.append(
                {
                    "id": Utility.GetColumn(self, idRow[0]),
                    "name": ModernWarfare.GetLocalize(self, tableRow[2]),
                    "flavor": ModernWarfare.GetLocalize(
                        self, tableRow[9].replace("STORE_FLAVOR/", "VEHICLES/")
                    ),
                    "type": ModernWarfare.GetLootType(self, int(idRow[0])),
                    "rarity": ModernWarfare.GetLootRarity(self, int(idRow[2])),
                    "season": ModernWarfare.GetLootSeason(self, int(idRow[5])),
                    "image": Utility.GetColumn(self, tableRow[7]),
                    "background": "ui_loot_bg_vehicle",
                }
            )

        status: bool = Utility.WriteFile(
            self, "export/Modern Warfare/", "vehicleCamos", "json", vehCamos
        )

        if status is True:
            log.info(f"Compiled {len(vehCamos):,} Vehicle Camos")

    def CompileWeapons(self: Any) -> None:
        """
        Compile the Weapon XAssets.
        
        Requires weapon_ids.csv and X_Y_variants.csv (for each Weapon)
        """

        ids: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "weapon_ids", "csv"
        )

        if ids is None:
            return

        weapons: dict = {}
        count: int = 0

        # TODO: Cleanup this mess...
        for idRow in ids:
            if weapons.get((w := Utility.GetColumn(self, idRow[1]))) is None:
                # Create the dictionary before we can populate it.
                weapons[w] = {}

                weapons[w]["id"] = Utility.GetColumn(self, idRow[0])
                weapons[w]["name"] = Utility.GetColumn(self, idRow[6])
                weapons[w]["description"] = (None,)  # This is determined later
                weapons[w]["flavor"] = (None,)  # This is determined later
                weapons[w]["type"] = ModernWarfare.GetLootType(self, int(idRow[0]))
                weapons[w]["rarity"] = ModernWarfare.GetLootRarity(self, int(idRow[2]))
                weapons[w]["image"] = (None,)  # This is determined later
                weapons[w]["icon"] = f"icon_cac_weapon_{str(w)[4:]}"
                weapons[w]["variants"] = []

                if w is not None:
                    weapons[w]["description"] = ModernWarfare.GetLocalize(
                        self, f"PERKS/{str(w)[4:].upper()}"
                    )

                if Utility.GetColumn(self, idRow[6]) is not None:
                    n = (
                        str(Utility.GetColumn(self, idRow[6]))[4:]
                        .upper()
                        .replace("VARIANT_", "")
                    )
                    weapons[w]["flavor"] = ModernWarfare.GetLocalize(
                        self, f"WEAPON_FLAVOR/{n}_FLAVOR"
                    )
            else:
                weapons[w]["variants"].append(
                    {
                        "id": Utility.GetColumn(self, idRow[0]),
                        "name": Utility.GetColumn(self, idRow[6]),
                        "description": None,  # This is determined later
                        "flavor": None,  # This is determined later
                        "type": ModernWarfare.GetLootType(self, int(idRow[0])),
                        "rarity": ModernWarfare.GetLootRarity(self, int(idRow[2])),
                        "season": ModernWarfare.GetLootSeason(self, int(idRow[5])),
                        "baseId": weapons[w]["id"],
                        "base": Utility.GetColumn(self, idRow[1]),
                        "image": None,  # This is determined later
                    }
                )

            count += 1

        for weapon in weapons:
            if (n := weapons[weapon]["name"]) is None:
                continue

            filename: str = Utility.FindBetween(self, n, "iw8_", "_variant")
            variants: self.csv = Utility.ReadFile(
                self, "import/Modern Warfare/Weapons/", f"{filename}_variants", "csv"
            )

            if variants is None:
                continue

            for varRow in variants:
                if Utility.GetColumn(self, varRow[1]) == n:
                    weapons[weapon]["name"] = ModernWarfare.GetLocalize(
                        self, varRow[17]
                    )
                    weapons[weapon]["image"] = Utility.GetColumn(self, varRow[18])

                    continue

                for variant in weapons[weapon]["variants"]:
                    if Utility.GetColumn(self, varRow[1]) is None:
                        continue

                    n: str = str(Utility.GetColumn(self, varRow[1]))

                    if n == variant["name"]:
                        variant["name"] = ModernWarfare.GetLocalize(self, varRow[17])
                        variant["image"] = Utility.GetColumn(self, varRow[18])

                        n: str = n[4:].replace("variant_", "").upper()
                        variant["flavor"] = ModernWarfare.GetLocalize(
                            self, f"WEAPON_FLAVOR/{n}_FLAVOR"
                        )

        status: bool = Utility.WriteFile(
            self, "export/Modern Warfare/", "weapons", "json", weapons
        )

        if status is True:
            log.info(f"Compiled {count:,} Weapons")

    def CompileWeaponUnlockChallenges(self: Any) -> None:
        """
        Compile the Weapon Unlock Challenge XAssets.

        Requires gun_unlock_challenges.csv
        """

        ids: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "gun_unlock_challenges", "csv"
        )

        if ids is None:
            return

        challenges: List[dict] = []

        for idRow in ids:
            challenges.append(
                {
                    "id": Utility.GetColumn(self, idRow[0]),
                    "name": ModernWarfare.GetLocalize(self, idRow[2]),
                    "description": ModernWarfare.GetLocalize(self, idRow[3]).replace(
                        "&&1", idRow[4]
                    ),
                    "amount": Utility.GetColumn(self, idRow[4]),
                    "weaponId": Utility.GetColumn(self, idRow[6]),
                }
            )

        status: bool = Utility.WriteFile(
            self, "export/Modern Warfare/", "weaponUnlockChallenges", "json", challenges
        )

        if status is True:
            log.info(f"Compiled {len(challenges):,} Weapon Unlock Challenges")

    def CompileWeeklyBRChallenges(self: Any) -> None:
        """
        Compile the Weekly Warzone Challenge XAssets.
        
        Requires br_weekly_challenges.csv
        """

        ids: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "br_weekly_challenges", "csv"
        )

        if ids is None:
            return

        count: int = 0
        challenges = {}

        # TODO: Cleanup this mess...
        for idRow in ids:
            s: str = str(Utility.GetColumn(self, idRow[1])).split("_")[3]

            if challenges.get(f"season{s}") is None:
                challenges[f"season{s}"] = {}

            w: str = str(Utility.GetColumn(self, idRow[1])).split("_")[5]

            if challenges[f"season{s}"].get(f"week{w}") is None:
                challenges[f"season{s}"][f"week{w}"] = []

            challenges[f"season{s}"][f"week{w}"].append(
                {
                    "id": Utility.GetColumn(self, idRow[0]),
                    "name": ModernWarfare.GetLocalize(self, idRow[2]),
                    "description": ModernWarfare.GetLocalize(self, idRow[3]).replace(
                        "&&1", idRow[4]
                    ),
                    "amount": Utility.GetColumn(self, idRow[4]),
                    "reward": Utility.GetColumn(self, idRow[5]),
                    "start": Utility.GetColumn(self, idRow[7]),
                    "end": Utility.GetColumn(self, idRow[8]),
                }
            )

            count += 1

        status: bool = Utility.WriteFile(
            self, "export/Modern Warfare/", "weeklyBRChallenges", "json", challenges
        )

        if status is True:
            log.info(f"Compiled {count:,} Weekly Warzone Challenges")

    def CompileWeeklyMPChallenges(self: Any) -> None:
        """
        Compile the Weekly Multiplayer Challenge XAssets.
        
        Requires weekly_challenges.csv
        """

        ids: self.csv = Utility.ReadFile(
            self, "import/Modern Warfare/", "weekly_challenges", "csv"
        )

        if ids is None:
            return

        count: int = 0
        challenges = {}

        for idRow in ids:
            s: str = str(Utility.GetColumn(self, idRow[1])).split("_")[2]

            if challenges.get(f"season{s}") is None:
                challenges[f"season{s}"] = {}

            w: str = str(Utility.GetColumn(self, idRow[1])).split("_")[4]

            if challenges[f"season{s}"].get(f"week{w}") is None:
                challenges[f"season{s}"][f"week{w}"] = []

            challenges[f"season{s}"][f"week{w}"].append(
                {
                    "id": Utility.GetColumn(self, idRow[0]),
                    "name": ModernWarfare.GetLocalize(self, idRow[2]),
                    "description": ModernWarfare.GetLocalize(self, idRow[3]).replace(
                        "&&1", idRow[4]
                    ),
                    "amount": Utility.GetColumn(self, idRow[4]),
                    "reward": Utility.GetColumn(self, idRow[5]),
                    "start": Utility.GetColumn(self, idRow[7]),
                    "end": Utility.GetColumn(self, idRow[8]),
                }
            )

            count += 1

        status: bool = Utility.WriteFile(
            self, "export/Modern Warfare/", "weeklyMPChallenges", "json", challenges
        )

        if status is True:
            log.info(f"Compiled {count:,} Weekly Multiplayer Challenges")

    def CompileDatabase(self: Any, outputImages: bool) -> None:
        """
        Compile the XAssets for the COD Tracker Database.

        https://cod.tracker.gg/modern-warfare/db/loot
        
        Requires accessories.json, battlePasses.json, callingCards.json, camos.json,
        charms.json, consumables.json, emblems.json, executions.json, quips.json,
        skins.json, specials.json, sprays.json, stickers.json, vehicleCamos.json,
        and weapons.json
        """

        # Database output files
        dbLoot: List[dict] = []
        dbBundles: List[dict] = []
        dbWeapons: List[dict] = []
        dbImages: List[str] = []

        include: List[str] = [
            "accessories.json",
            "battlePasses.json",
            "callingCards.json",
            "camos.json",
            "charms.json",
            "consumables.json",
            "emblems.json",
            "executions.json",
            "features.json",
            "quips.json",
            "skins.json",
            "specialItems.json",
            "sprays.json",
            "stickers.json",
            "vehicleCamos.json",
        ]

        for file in glob("export/Modern Warfare/*.json"):
            if (filename := file.rsplit("\\")[1]) not in include:
                continue

            loot: self.json = Utility.ReadFile(
                self, "export/Modern Warfare/", filename.split(".")[0], "json"
            )

            if loot is None:
                log.error(f"{filename} not found in /export/Modern Warfare/")

                continue

            for item in loot:
                if item.get("name") is None:
                    continue

                if (image := item.get("image")) is None:
                    continue

                dbImages.append(image)

                if (
                    Utility.CheckExists(
                        self, "import/Modern Warfare/Images/", image, "png"
                    )
                    is False
                ):
                    if item.get("type") != "Battle Pass":
                        continue

                item["animated"] = Utility.AnimateSprite(
                    self,
                    "import/Modern Warfare/Images/",
                    image,
                    "png",
                    item.get("type"),
                    outputImages,
                )

                dbLoot.append(item)

        bundles: self.json = Utility.ReadFile(
            self, "export/Modern Warfare/", "bundles", "json"
        )

        for bundle in bundles:
            if bundle.get("name") is None:
                continue

            if (billboard := bundle.get("billboard")) is None:
                continue

            if (logo := bundle.get("logo")) is None:
                continue

            dbImages.append(billboard)
            dbImages.append(logo)

            if (
                Utility.CheckExists(
                    self, "import/Modern Warfare/Images/", billboard, "png"
                )
                is False
            ):
                continue

            if (
                Utility.CheckExists(self, "import/Modern Warfare/Images/", logo, "png")
                is False
            ):
                continue

            items: List[int] = []

            for item in bundle.get("items", []):
                items.append(item.get("id"))

            bundle["items"] = items

            dbBundles.append(bundle)

        weapons: self.json = Utility.ReadFile(
            self, "export/Modern Warfare/", "weapons", "json"
        )

        for weapon in weapons:
            if weapons[weapon].get("name") is None:
                continue

            if (image := weapons[weapon].get("image")) is None:
                continue

            if (icon := weapons[weapon].get("icon")) is not None:
                dbImages.append(icon)

            dbImages.append(image)

            if (
                Utility.CheckExists(self, "import/Modern Warfare/Images/", image, "png")
                is False
            ):
                continue

            variants: List[int] = []

            for variant in weapons[weapon]["variants"]:
                if variant.get("name") is None:
                    continue

                if (image := variant.get("image")) is None:
                    continue

                dbImages.append(image)

                if (
                    Utility.CheckExists(
                        self, "import/Modern Warfare/Images/", image, "png"
                    )
                    is False
                ):
                    continue

                dbLoot.append(variant)
                variants.append(variant.get("id"))

            weapons[weapon]["variants"] = variants

            dbWeapons.append(weapons[weapon])

        Utility.WriteFile(
            self,
            "export/Modern Warfare/DB/",
            "loot",
            "json",
            Utility.SortList(self, dbLoot, "name"),
            compress=False,
        )

        Utility.WriteFile(
            self,
            "export/Modern Warfare/DB/",
            "bundles",
            "json",
            Utility.SortList(self, dbBundles, "name"),
            compress=False,
        )

        Utility.WriteFile(
            self,
            "export/Modern Warfare/DB/",
            "weapons",
            "json",
            Utility.SortList(self, dbWeapons, "name"),
            compress=False,
        )

        Utility.WriteFile(
            self,
            "export/Modern Warfare/DB/",
            "_search",
            "txt",
            ",".join(list(set(dbImages))),
        )

        count: int = len(dbLoot) + len(dbWeapons) + len(dbBundles)
        log.info(f"Compiled {count:,} Database Items")
