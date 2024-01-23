from mutantfuture.characters import CharacterBase
import random
import json
from config import RULEBOOK_PATH, ALIGNMENTS, SPLAT_COUNT
import uuid


def main():
    player_name = None
    while player_name == None:
        player_name = input('Player name? ').strip()
        if len(player_name) > 12:
            print('Max 12 characters for player name please.\n')
            player_name = None
            continue
            
        if not player_name.isalnum():
            print('Alphanumeric characters only please.\n')
            player_name = None
            continue

    characters = []

    for _ in range(0, SPLAT_COUNT):
        new_character = get_random_character()
        characters.append(new_character)

    create_characters_file(characters, player_name)


def get_random_character():
    rulebook = get_rulebook(RULEBOOK_PATH)
    character = CharacterBase()

    #strength
    character.strength = roll_dice('3d6')
    character.strength_mod = get_mod_by_attr_value(rulebook['strengthModSets'], 'str_mod', character.strength)
    character.damage_mod = get_mod_by_attr_value(rulebook['strengthModSets'], 'dmg_mod', character.strength)

    #dexterity
    character.dexterity = roll_dice('3d6')
    character.ac_mod = get_mod_by_attr_value(rulebook['dexterityModSets'], 'ac_mod', character.dexterity)
    character.missile_mod = get_mod_by_attr_value(rulebook['dexterityModSets'], 'missile_mod', character.dexterity)
    character.init_mod = get_mod_by_attr_value(rulebook['dexterityModSets'], 'init_mod', character.dexterity)

    #constitution
    character.constitution = roll_dice('3d6')
    character.poison_death_mod = get_mod_by_attr_value(rulebook['constitutionModSets'], 'poison_death_mod', character.constitution)
    character.radiation_mod = get_mod_by_attr_value(rulebook['constitutionModSets'], 'radiation_mod', character.constitution)

    #intelligence
    character.intelligence = roll_dice('3d6')
    character.technology_mod = get_mod_by_attr_value(rulebook['intelligenceModSets'], 'tech_mod', character.intelligence)

    #willpower
    character.willpower = roll_dice('3d6')

    #charisma
    character.charisma = roll_dice('3d6')
    character.reaction_mod = get_mod_by_attr_value(rulebook['charismaModSets'], 'reaction_mod', character.charisma)
    character.retainers = get_mod_by_attr_value(rulebook['charismaModSets'], 'retainers', character.charisma)
    character.retainer_morale = get_mod_by_attr_value(rulebook['charismaModSets'], 'retainer_morale', character.charisma)

    #saves
    character.energy_save = 15
    character.poison_death_save = 12
    character.stun_save = 14
    character.radiation_save = 13

    #alignment
    character.alignment = get_random_alignment()

    #race
    character.race = get_random_race(rulebook)

    #mutations
    character.mutations = get_character_mutations(rulebook, character.race)

    #feats
    character.feats = random.choice(rulebook['feats'])['fields']

    #backgrounds
    character.backgrounds = random.choice(rulebook['backgrounds'])['fields']

    #thac0
    character.thac0 = 19

    #gold
    character.gold = 10 * roll_dice('3d8')

    #hit points
    character.hit_points = get_hit_points(character.race, character.constitution)
    
    return character


def get_random_alignment():
    return random.choice(ALIGNMENTS)


def get_random_race(rulebook):
    #filter out base versions for now
    filtered_races = list(filter(lambda race : '(base)' not in race['fields']['name'].lower(), rulebook['races']))
    return random.choice(filtered_races)['fields']


def get_mutation_by_pk(rulebook, mutation_id):
    all_mutations = rulebook['mutations']
    return list(filter(lambda mutation: mutation['pk'] == mutation_id, all_mutations))[0]


def get_character_mutations(rulebook, character_race):
    all_mutations = rulebook['mutations']
    character_mutations = []

    #mental mutations
    total_new_mutations = roll_dice(character_race['mental_mutations_roll_str'])
    if (total_new_mutations > 0):
        mutation_list = []
        for mutation in all_mutations:
            if mutation['fields']['type'] == 'mental':
                mutation_list.append(mutation)
        
        character_mutations = append_random_mutations(character_mutations, total_new_mutations, mutation_list)
    

    #physical mutations
    total_new_mutations = roll_dice(character_race['physical_mutations_roll_str'])
    if (total_new_mutations > 0):
        mutation_list = []
        for mutation in all_mutations:
            if mutation['fields']['type'] == 'physical':
                mutation_list.append(mutation)
        
        character_mutations = append_random_mutations(character_mutations, total_new_mutations, mutation_list)


    #plant_mutations
    total_new_mutations = roll_dice(character_race['plant_mutations_roll_str'])
    if (total_new_mutations > 0):
        mutation_list = []
        for mutation in all_mutations:
            if mutation['fields']['type'] == 'plant':
                mutation_list.append(mutation)
        
        character_mutations = append_random_mutations(character_mutations, total_new_mutations, mutation_list)


    #random_human_animal_mutations
    total_new_mutations = roll_dice(character_race['random_human_animal_roll_str'])
    if (total_new_mutations > 0):
        mutation_list = []
        for mutation in all_mutations:
            if mutation['fields']['type'] == 'mental' or mutation['fields']['type'] == 'physical':
                mutation_list.append(mutation)
        
        character_mutations = append_random_mutations(character_mutations, total_new_mutations, mutation_list)


    #random_beneficial_any_mutations
    total_new_mutations = roll_dice(character_race['random_beneficial_any_roll_str'])
    if (total_new_mutations > 0):
        mutation_list = []
        for mutation in all_mutations:
            if mutation['fields']['effect_type'] == 'benefit':
                mutation_list.append(mutation)
        
        character_mutations = append_random_mutations(character_mutations, total_new_mutations, mutation_list)


    #special_animal_mutations
    total_new_mutations = roll_dice(character_race['special_animal_roll_str'])
    if (total_new_mutations > 0):
        character_mutations = append_random_special_mutations(character_mutations, total_new_mutations, rulebook['specialAnimalMutationRolls'], rulebook)


    #special_insect_mutations
    total_new_mutations = roll_dice(character_race['special_insect_roll_str'])
    if (total_new_mutations > 0):
        character_mutations = append_random_special_mutations(character_mutations, total_new_mutations, rulebook['specialInsectMutationRolls'], rulebook)


    #mental_drawback_mutations
    total_new_mutations = roll_dice(character_race['mental_drawback_roll_str'])
    if (total_new_mutations > 0):
        mutation_list = []
        for mutation in all_mutations:
            if mutation['fields']['effect_type'] == 'drawback' and mutation['fields']['type'] == 'mental':
                mutation_list.append(mutation)
        
        character_mutations = append_random_mutations(character_mutations, total_new_mutations, mutation_list)


    #physical_drawback_mutations
    total_new_mutations = roll_dice(character_race['physical_drawback_roll_str'])
    if (total_new_mutations > 0):
        mutation_list = []
        for mutation in all_mutations:
            if mutation['fields']['effect_type'] == 'drawback' and mutation['fields']['type'] == 'physical':
                mutation_list.append(mutation)
        
        character_mutations = append_random_mutations(character_mutations, total_new_mutations, mutation_list)


    #random_any_mutations
    total_new_mutations = roll_dice(character_race['random_any_roll_str'])
    if (total_new_mutations > 0):
        
        mutation_count = 0
        while mutation_count < total_new_mutations:
            mutation_name = get_full_mutation_name(random.choice(all_mutations))
            if mutation_name not in character_mutations:
                character_mutations.append(mutation_name)
                mutation_count += 1

    return character_mutations


def append_random_mutations(character_mutations, total_new_mutations, mutation_list):
        mutation_count = 0
        while mutation_count < total_new_mutations:
            mutation_name = get_full_mutation_name(random.choice(mutation_list))
            if mutation_name not in character_mutations:
                character_mutations.append(mutation_name)
                mutation_count += 1

        return character_mutations


def append_random_special_mutations(character_mutations, total_new_mutations, mutation_list, rulebook):
        mutation_count = 0
        while mutation_count < total_new_mutations:
            random_mutation_pk = random.choice(mutation_list)['fields']['mutation']
            random_mutation = get_mutation_by_pk(rulebook, random_mutation_pk)
            mutation_name = get_full_mutation_name(random_mutation)
            if mutation_name not in character_mutations:
                character_mutations.append(mutation_name)
                mutation_count += 1

        return character_mutations


def get_full_mutation_name(mutation):
    return f"{mutation['fields']['name']} ({mutation['fields']['type']}, {mutation['fields']['effect_type']}, {mutation['fields']['page_number']})"


def roll_dice(roll_str):
    if 'd' in roll_str.lower():
        total = 0
        num_dice, num_sides = roll_str.split('d')
        num_dice = int(num_dice)
        num_sides = int(num_sides)

        for _ in range(1, num_dice+1):
            total += random.randint(1,num_sides)
        
        return total
    else:
        return int(roll_str)
    

def get_rulebook(json_file_path):
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
            return data[0]
    except FileNotFoundError:
        raise


def get_mod_by_attr_value(attribute_table, mod_name, value):
    value_row = list(filter(lambda row : row['fields']['value'] == value, attribute_table))[0]
    return value_row['fields'][mod_name]


def get_hit_points(race, constitution_value):
    fixed_hp_races = ['synthetic android', 'basic android']
    if race['name'].lower() in fixed_hp_races:
        return 50
    else:
        sides = race['hit_dice_sides']
        return roll_dice(f'{constitution_value}d{sides}')
    

def get_splat_sheet_string(characters, player_name='', for_html=False):
    splat_sheet_contents = 'MUTANT FUTURE CHARACTER SPLAT'
    if player_name != '':
        splat_sheet_contents += f' FOR PLAYER {player_name.upper()}'
    splat_sheet_contents += '\n\n'

    chararacter_number = 1
    for character in characters:
        splat_sheet_contents += f'---------------start record {chararacter_number} of {len(characters)}---------------\n'
        splat_sheet_contents += f'Race: {character.race["name"]} ({character.race["page_number"]})\n'
        splat_sheet_contents += f'Background: {character.backgrounds["name"]}\n'
        splat_sheet_contents += f'Alignment: {character.alignment}\n'

        splat_sheet_contents += '\n'
        splat_sheet_contents += f'Strength: {character.strength}\n'
        splat_sheet_contents += f'--Strength Mod: {character.strength_mod}\n'
        splat_sheet_contents += f'--Damage Mod: {character.damage_mod}\n'
        splat_sheet_contents += '\n'
        splat_sheet_contents += f'Dexterity: {character.dexterity}\n'
        splat_sheet_contents += f'-- AC Mod: {character.ac_mod}\n'
        splat_sheet_contents += f'-- Missile Mod: {character.missile_mod}\n'
        splat_sheet_contents += f'-- Init Mod: {character.init_mod}\n'
        splat_sheet_contents += '\n'
        splat_sheet_contents += f'Constitution: {character.constitution}\n'
        splat_sheet_contents += f'--Poison Save Mod: {character.poison_death_mod}\n'
        splat_sheet_contents += f'--Poison Save Mod: {character.radiation_mod}\n'
        splat_sheet_contents += '\n'
        splat_sheet_contents += f'Intelligence: {character.intelligence}\n'
        splat_sheet_contents += f'--Technology Mod: {character.technology_mod}\n'
        splat_sheet_contents += '\n'
        splat_sheet_contents += f'Willpower: {character.willpower}\n'
        splat_sheet_contents += '\n'
        splat_sheet_contents += f'Charisma: {character.charisma}\n'
        splat_sheet_contents += f'--Reaction Mod: {character.reaction_mod}\n'
        splat_sheet_contents += f'--Retainers: {character.retainers}\n'
        splat_sheet_contents += f'--Retainer Morale: {character.retainer_morale}\n'
        splat_sheet_contents += '\n'
        splat_sheet_contents += f'Hit Points: {character.hit_points}\n'
        splat_sheet_contents += '\n'

        if len(character.mutations) > 0:
            splat_sheet_contents += f'Mutations:\n'
            for mutation in character.mutations:
                splat_sheet_contents += f'--{mutation}\n'
        else:
            splat_sheet_contents += f'Mutations: None\n'

        splat_sheet_contents += '\n'
        splat_sheet_contents += f'Feat: {character.feats["name"]} ({character.feats["page_number"]})\n'
        splat_sheet_contents += f'\n'
        splat_sheet_contents += f'Gold: {character.gold}\n'
        splat_sheet_contents += f'\n'
        splat_sheet_contents += f'Saving Throws\n'
        splat_sheet_contents += f'--Energy Save: {character.energy_save}\n'
        splat_sheet_contents += f'--Poison/Death Save: {character.poison_death_save}\n'
        splat_sheet_contents += f'--Stun Save: {character.stun_save}\n'
        splat_sheet_contents += f'--Radiation Save: {character.radiation_save}\n'
        splat_sheet_contents += f'\n'
        splat_sheet_contents += f'----------------end record {chararacter_number} of {len(characters)}----------------\n'
        splat_sheet_contents += f'\n'
        chararacter_number += 1

    if for_html:
        splat_sheet_contents = splat_sheet_contents.replace('\n','<br>')

    return splat_sheet_contents
        

def create_characters_file(characters, player_name):
    with open(f'splat_sheets/characters_splat_{player_name}_{uuid.uuid4()}.txt', 'w') as text_file:
        text_file_contents = get_splat_sheet_string(characters)
        text_file.write(text_file_contents)


if __name__ == '__main__':
    main()