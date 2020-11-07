import argparse

from randovania.game_description import data_reader
from randovania.game_description.node import PickupNode
from randovania.games.game import RandovaniaGame
from randovania.games.prime import default_data

_TEMPLATE = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ(){}[]<>=,.!#^-+?"

letter_to_item_mapping = {
    "0": ["Power Beam"],
    "1": ["Plasma Beam"],
    "2": ["Nova Beam"],
    "3": ["ChargeUpgrade"],
    "4": ["Missile"],
    "5": ["IceMissile"],
    "6": ["SeekerMissile"],
    "7": ["GrapleBeamPull"],
    "8": ["GrappleBeamSwing"],
    "9": ["GrappleBeamVoltage"],
    "a": ["Bomb"],
    "b": ["CombatVisor"],
    "c": ["ScanVisor"],
    "d": ["CommandVisor"],
    "e": ["XRayVisor"],
    "f": ["DoubleJump"],
    "g": ["ScrewAttack"],
    "h": ["SuitType"],
    "i": ["Energy"],
    "j": ["HyperModeEnergy"],
    "k": ["EnergyTank"],
    "l": ["ItemPercentage"],
    "m": ["Fuses"],
    "n": ["Fuse1"],
    "o": ["Fuse2"],
    "p": ["Fuse3"],
    "q": ["Fuse4"],
    "r": ["Fuse5"],
    "s": ["Fuse6"],
    "t": ["Fuse7"],
    "u": ["Fuse8"],
    "v": ["Fuse9"],
    "w": ["MorphBall"],
    "x": ["BoostBall"],
    "y": ["SpiderBall"],
    "z": ["HyperModeTank"],
    "A": ["HyperModeBeam"],
    "B": ["HyperModeMissile"],
    "C": ["HyperModeBall"],
    "D": ["HyperModeGrapple"],
    "E": ["HyperModePermanent"],
    "F": ["HyperModePhaaze"],
    "G": ["HyperModeOriginal"],
    "H": ["ShipGrapple"],
    "I": ["ShipMissileExpansion"],
    "J": ["FaceCorruptionLevel"],
    "K": ["PhazonBall"],
    "L": ["CannonBall"],
    "M": ["ActivateMorphballBoost"],
    "N": ["HyperShot"],
    "O": ["CommandVisorJammed"],
    "P": ["Stat_Enemies_Killed"],
    "Q": ["Stat_ShotsFired"],
    "R": ["Stat_DamageReceived"],
    "S": ["Stat_DataSaves"],
    "T": ["Stat_HypermodeUses"],
    "U": ["Stat_CommandoKills"],
    "V": ["Stat_TinCanHighScore"],
    "W": ["Stat_TinCanCurrentScore"],
    "X": ["Missile"] * 2,
    "Y": ["Missile"] * 3,
    "Z": ["Missile"] * 4,
    "(": ["Missile"] * 5,
    ")": ["Missile"] * 6,
    "{": ["Missile"] * 7,
    "}": ["Missile"] * 8,
    "[": ["EnergyTank", "EnergyTank"],
    "]": ["EnergyTank", "EnergyTank", "EnergyTank"],
    "<": ["ShipMissileExpansion", "ShipMissileExpansion"],
    ">": ["Missile", "EnergyTank"],
    "=": ["EnergyTank", "Missile"],
    ",": ["Missile", "EnergyTank", "Missile"],
    ".": ["Missile", "ShipMissileExpansion"],
    "!": ["ShipMissileExpansion", "Missile"],
    "#": ["Missile Launcher"],
    "^": ["Main Ship Missiles"],
    "-": ["ShipMissileExpansion", "EnergyTank"],
    "+": ["EnergyTank", "ShipMissileExpansion"],
    "?": ["Missile", "ShipMissileExpansion", "Missile"],
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("layout")
    args = parser.parse_args()

    game = data_reader.decode_data(default_data.read_json_then_binary(RandovaniaGame.PRIME3)[1])
    pickup_nodes = [node for node in game.world_list.all_nodes if isinstance(node, PickupNode)]

    layout_string = args.layout

    sha_hash = layout_string[-5:]
    initial_rot = _TEMPLATE.index(layout_string[0])
    extra_rot = _TEMPLATE.index(layout_string[1])
    items_str = layout_string[2:-5]

    current_rot = initial_rot

    items = []
    for s in items_str:
        new_index = _TEMPLATE.index(s) - current_rot
        correct_letter = _TEMPLATE[new_index % len(_TEMPLATE)]
        items.extend(letter_to_item_mapping[correct_letter])

        current_rot = (current_rot + extra_rot) % len(_TEMPLATE)

    for node in pickup_nodes:
        print("{}: {}".format(
            game.world_list.node_name(node, with_world=True),
            items[node.pickup_index.index]
        ))


if __name__ == '__main__':
    main()
