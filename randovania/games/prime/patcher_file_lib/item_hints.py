from random import Random
from typing import Dict, Tuple, List, Optional

from randovania.game_description.assignment import PickupAssignment
from randovania.game_description.game_patches import GamePatches
from randovania.game_description.hint import HintType, HintLocationPrecision, HintItemPrecision, Hint
from randovania.game_description.node import LogbookNode
from randovania.game_description.resources.pickup_entry import PickupEntry
from randovania.game_description.resources.pickup_index import PickupIndex
from randovania.game_description.world_list import WorldList
from randovania.games.prime.patcher_file_lib.hint_name_creator import LocationHintCreator, create_simple_logbook_hint, \
    color_text, TextColor


class CaseFormatString(str):
    def __format__(self, fmt):
        s = str(self)
        if len(fmt) > 0:
            if fmt[0] == 'u':
                s = self.upper()
                fmt = fmt[1:]
            elif fmt[0] == 'l':
                s = self.lower()
                fmt = fmt[1:]
            elif fmt[0] == 't':
                s = self.title()
                fmt = fmt[1:]
        return s.__format__(fmt)


# Guidelines for joke hints:
# 1. They should clearly be jokes, and not real hints or the result of a bug.
# 2. They shouldn't reference real-world people.
# 3. They should be understandable by as many people as possible.
_JOKE_HINTS = [
    "By this point in your run, you should have consumed at least 200 mL of water to maintain optimum hydration.",
    "Make sure to collect an Energy Transfer Module; otherwise your run won't be valid!",
    "Adam has not yet authorized the use of this hint.",
    "Back in my day, we didn't need hints!",
    "Hear the words of O-Lir, last Sentinel of the Fortress Temple. May they serve you well.",
    "Warning! Dark Aether's atmosphere is dangerous! Energized Safe Zones don't last forever!",
    "A really important item can be found at - (transmission ends)",
]

_PRIME_1_ITEMS = [
    "Varia Suit",
    "Wave Beam",
    "Thermal Visor",
    "Wavebuster",
    "Ice Beam",
    "Gravity Suit",
    "X-Ray Visor",
    "Ice Spreader",
    "Plasma Beam",
    "Flamethrower",
    "Phazon Suit",
]

_PRIME_3_ITEMS = [
    "Grapple Lasso",
    "PED Suit",
    "Grapple Swing",
    "Ice Missile",
    "Ship Missile Launcher",
    "Hyper Ball",
    "Plasma Beam",
    "Ship Grapple Beam",
    "Hyper Missile",
    "X-Ray Visor",
    "Grapple Voltage",
    "Hazard Shield",
    "Nova Beam",
    "Hyper Grapple",
]

_PRIME_1_LOCATIONS = [
    "Hive Totem",
    "Ruined Shrine",
    "Burn Dome",
    "Sunchamber",
    "Quarantine Cave",
    "Gravity Chamber",
    "Elite Research",
    "Life Grove",
    "Phendrana Shorelines",
    "Plasma Processing",
    "Elite Quarters",
]

_PRIME_3_LOCATIONS = [
    "Docking Hub Alpha",
    "Command Vault",
    "Proving Grounds",
    "Temple of Bryyo",
    "Tower",
]

_DET_AN = [
    "Annihilator Beam",
    "Amber Translator",
    "Echo Visor",
    "Emerald Translator",
    "Energy Transfer Module",
    "Energy Tank",
]

_DET_NULL = []
for i in range(1, 4):
    _DET_NULL.extend([f"Dark Agon Key {i}", f"Dark Torvus Key {i}", f"Ing Hive Key {i}"])
for i in range(1, 10):
    _DET_NULL.append(f"Sky Temple Key {i}")

_GUARDIAN_NAMES = {
    PickupIndex(43): "Amorbis",
    PickupIndex(79): "Chykka",
    PickupIndex(115): "Quadraxis",
}

_HINT_MESSAGE_TEMPLATES = {
    HintType.KEYBEARER: "The Flying Ing Cache in {location} contains {determiner}{pickup}.",
    HintType.GUARDIAN: "{location} is guarding {determiner}{pickup}.",
    HintType.LIGHT_SUIT_LOCATION: "U-Mos's reward for returning the Sanctuary energy is {determiner}{pickup}.",
    HintType.LOCATION: "{determiner:t}{pickup} can be found in {location}.",
}


class ItemHintCreator:
    def __init__(self, patches: GamePatches, world_list: WorldList):
        self.hint_name_creator = LocationHintCreator(world_list)
        self.joke_items = sorted(set(_PRIME_1_ITEMS) | set(_PRIME_3_ITEMS))
        self.joke_locations = sorted(set(_PRIME_1_LOCATIONS) | set(_PRIME_3_LOCATIONS))
        self.joke_hints = sorted(_JOKE_HINTS)
        self.patches = patches

    def shuffle_jokes(self, rng: Random):
        rng.shuffle(self.joke_items)
        rng.shuffle(self.joke_locations)
        rng.shuffle(self.joke_hints)

    def _calculate_location_hint(self, hint: Hint) -> str:
        if hint.hint_type is HintType.GUARDIAN:
            location_name = color_text(TextColor.GUARDIAN, _GUARDIAN_NAMES[hint.target])

        elif hint.location_precision == HintLocationPrecision.WRONG_GAME:
            location_name = color_text(TextColor.JOKE,
                                       "{} (?)".format(self.joke_locations.pop())
                                       if self.joke_locations
                                       else "an unknown location")
        else:
            hide_area = hint.location_precision != HintLocationPrecision.DETAILED
            location_name = color_text(TextColor.LOCATION,
                                       self.hint_name_creator.index_node_name(hint.target, hide_area))
        return location_name

    def _calculate_pickup_determiner(self, pickup: PickupEntry) -> str:
        pickup_assignment = self.patches.pickup_assignment

        if pickup.name in _DET_NULL:
            determiner = ""
        elif tuple(pickup_entry.name for pickup_entry in pickup_assignment.values()).count(pickup.name) == 1:
            determiner = "the "
        elif pickup.name in _DET_AN:
            determiner = "an "
        else:
            determiner = "a "

        return determiner

    def _calculate_pickup_hint(self,
                               precision: HintItemPrecision,
                               pickup: Optional[PickupEntry],
                               ) -> Tuple[bool, str, str]:
        if pickup is None:
            if len(self.patches.pickup_assignment) == 118:
                determiner = "the "
            else:
                determiner = "an "
            return False, determiner, "Energy Transfer Module"

        if precision is HintItemPrecision.WRONG_GAME:
            return True, "the ", self.joke_items.pop() + " (?)"

        elif precision is HintItemPrecision.GENERAL_CATEGORY:
            if pickup.item_category.is_major_category:
                return False, "a ", "major upgrade"
            elif pickup.item_category.is_key:
                return False, "a ", "Dark Temple Key"
            else:
                return False, "an ", "expansion"

        elif precision is HintItemPrecision.PRECISE_CATEGORY:
            details = pickup.item_category.hint_details
            return False, details[0], details[1]

        else:
            return False, self._calculate_pickup_determiner(pickup), pickup.name

    def get_message_for(self, rng: Random, hint: Hint) -> str:
        if hint.precision.is_joke:
            if not self.joke_hints:
                joke_hints = sorted(_JOKE_HINTS)
                rng.shuffle(joke_hints)
            return color_text(TextColor.JOKE, self.joke_hints.pop())

        else:
            pickup = self.patches.pickup_assignment.get(hint.target)

            # Determine location name
            location_name = self._calculate_location_hint(hint)

            # Determine pickup name
            is_joke, determiner, pickup_name = self._calculate_pickup_hint(
                hint.item_precision,
                pickup,
            )
            pickup_name = color_text(TextColor.JOKE if is_joke else TextColor.ITEM, pickup_name)

            return _HINT_MESSAGE_TEMPLATES[hint.hint_type].format(determiner=CaseFormatString(determiner),
                                                                  pickup=pickup_name,
                                                                  location=location_name)


def create_hints(patches: GamePatches,
                 world_list: WorldList,
                 rng: Random,
                 ) -> list:
    """
    Creates the string patches entries that changes the Lore scans in the game for item pickups
    :param patches:
    :param world_list:
    :param rng:
    :return:
    """

    hint_creator = ItemHintCreator(patches, world_list)
    hint_creator.shuffle_jokes(rng)

    hints_for_asset: Dict[int, str] = {
        asset.asset_id: hint_creator.get_message_for(rng, hint)
        for asset, hint in patches.hints.items()
    }

    return [
        create_simple_logbook_hint(
            logbook_node.string_asset_id,
            hints_for_asset.get(logbook_node.string_asset_id, "Someone forgot to leave a message."),
        )
        for logbook_node in world_list.all_nodes
        if isinstance(logbook_node, LogbookNode)
    ]


def hide_hints(world_list: WorldList) -> list:
    """
    Creates the string patches entries that changes the Lore scans in the game
    completely useless text.
    :return:
    """

    return [create_simple_logbook_hint(logbook_node.string_asset_id, "Some item was placed somewhere.")
            for logbook_node in world_list.all_nodes if isinstance(logbook_node, LogbookNode)]
