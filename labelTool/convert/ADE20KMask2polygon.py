
# coding: utf-8

import numpy as np
import os
import sys

import cv2

sys.path.append( os.path.normpath( os.path.join( os.path.dirname( __file__ ) , '..') ) )
from helper.annotation import Point, Annotation, CsObject

ADE20KLabel = ['-',  '-', 'aarm panel',    'abacus',    'accordion, piano accordion, squeeze box',   'acropolis',
               'ad, advertisement, advertizement, advertising, advertizing, advert', 'adding machine',
               'advertisement board',    'aerial',    'air conditioner, air conditioning', 'air hockey table',
               'air machine',    'aircraft carrier',  'airplane, aeroplane, plane',    'airport cart',  'alarm',
               'alarm clock',    'alembic',   'alga',  'algae', 'altar, communion table, Lord''s table', 'altarpiece',
               'amphitheater',   'amphora',   'anchor',    'andiron',   'andirons',  'animal toy',
               'animal, animate being, beast, brute, creature, fauna',   'animals',   'antenna',
               'antenna, aerial, transmitting aerial',   'antler',    'antlers',   'anvil', 'aperture',
               'apparatus',  'apparel, wearing apparel, dress, clothes',  'apple', 'apples',    'appliance', 'apron',
               'aquarium',   'aqueduct',  'arbor', 'arcade',    'arcade machine',    'arcade machines',   'arcade, colonnade',
               'arcades',    'arch',  'arch, archway', 'arches',    'arm',   'arm panel', 'arm support',   'armchair',  'armor',
               'armrest',    'art',   'art mannequin', 'articulated lamp',  'artificial golf green',
               'ashcan, trash can, garbage can, wastebin, ash bin, ash-bin, ashbin, dustbin, trash barrel, trash bin',
               'ashtray',    'asymmetric bars',   'athletic field',    'athletics track',   'atm',   'autoclave',
               'autopsy table',  'auxiliary trolley', 'aviary',    'avocados',  'award', 'awards',
               'awning, sunshade, sunblind', 'ax',    'baby buggy, baby carriage, carriage, perambulator, pram, stroller, go-cart, pushchair, pusher',
               'baby chair', 'baby walker',   'baby weighs',   'back',  'back control',  'back cushion',  'back pillow',
               'backdrop',   'backdrops', 'background',    'backpack, back pack, knapsack, packsack, rucksack, haversack',
               'backpacks',  'backplate', 'badge', 'badlands',  'bag',   'bag, handbag, pocketbook, purse',
               'bag, traveling bag, travelling bag, grip, suitcase', 'baggage',   'baggage carts', 'bagpipes',  'balcony',
               'balcony covered',    'ball',  'ball rack', 'ball stands',   'ball storage',  'ball, globe, orb',  'balloon',
               'balloons',   'ballots',   'balls rack',    'balustrade',    'bamboo',    'bamboo canes',  'bananas',   'bandstand',
               'banjo',  'banner, streamer',  'banners',   'bannister, banister, balustrade, balusters, handrail',
               'baptismal font', 'baptistry', 'bar',   'bar lift',  'barbecue',  'barbed wire',   'barbell',   'barn',
               'barrack buildings',  'barrel rack',   'barrel, cask',  'barrels',   'barricade', 'barrier',   'bars',  'base',
               'base, pedestal, stand',  'baseball',  'baseball glove',    'baseboard', 'baseboard, mopboard, skirting board',
               'baseboards', 'basin', 'basket',    'basket, basketball hoop, hoop', 'basket, handbasket',    'basketball',
               'basketball court',   'baskets',   'bass drum', 'bassinet',  'bat',   'bath sponge',   'bathrobe',
               'bathtub, bathing tub, bath, tub',    'batting cage',  'battlement',    'battlements',   'beach wrap',
               'beacon, lighthouse, beacon light, pharos',   'beam',  'beams', 'bear',  'bear cutout',   'bed',   'bed column',
               'bed side',   'bed trolley',   'bedpost',   'beds',  'bedspread', 'bedspring', 'beer machine',  'beer pump', 'bell',
               'bell tower', 'belt',  'belt loader',   'belt rack', 'belts', 'bench', 'berth', 'bib',   'bicycle path',
               'bicycle rack',   'bicycle racks', 'bicycle, bike, wheel, cycle',   'bidet', 'bidon', 'big top',   'big wheel',
               'bilding',    'bildings',  'billboard, hoarding',   'bin',   'binder, ring-binder',   'binoculars',    'bird',
               'birdcage',   'birds', 'bitch', 'blackboard, chalkboard',    'blade', 'blade, vane',   'blades',
               'blanket, cover', 'blankets',  'blast furnace', 'bleachers', 'blender',   'blind', 'blind, screen', 'blinds',
               'block',  'blocks',    'blouse',    'blusher brush', 'boar',  'board game',    'board, plank',  'boards',
               'boardwalk',  'boat',  'boat stop', 'body',  'bog water', 'boiler',    'boillers',  'bollard',   'bolt',  'bomb',
               'bone',   'bones', 'bonfire',   'bonnet',    'book',  'book rack', 'book stand',    'bookcase',  'bookend',
               'bookends',   'booklet, brochure, folder, leaflet, pamphlet',  'bookstall', 'boomerang', 'boot',  'booth',
               'booth, cubicle, stall, kiosk',   'booths',    'bottle',    'bottle pack',   'bottle rack',   'bottom rail',
               'bough',  'boulder',   'bounce seat',   'bouquet, corsage, posy, nosegay',   'bow',   'bow window',    'bowl',
               'bowling alley',  'bowling alleys',    'bowling ball return',   'bowling pin',   'bowling pins',  'bowls',
               'box',    'box jury',  'box office, ticket office, ticket booth',   'box spring',    'box stands',
               'box-file',   'boxing gloves', 'bracelet',  'bracelets', 'bracket',   'brake pedal',   'branch',    'branches',
               'bread basket',   'bread box', 'bread lift',    'bread roll',    'bread rolls',   'bread slot',    'bread tray',
               'bread, breadstuff, staff of life',   'breadbasket',   'breads',    'breaker box',   'breakwater',    'brewery',
               'brick',  'bricks',    'bridge, span',  'bridges',   'briefcase', 'brochure',  'brochures rack',    'broom',
               'brush',  'brushes',   'bucket',    'bucket, pail',  'buckets',   'bud',   'buds',  'buffet',
               'buffet, counter, sideboard', 'buggy', 'building arena',    'building materials',    'building, edifice',
               'bulb',   'bulbs', 'bull',  'bull skull',    'bulldozer', 'bulletin board, notice board',  'bullring',  'bumper',
               'bunch',  'buoy',  'buoys', 'burner',    'bus station',   'bus stop',
               'bus, autobus, coach, charabanc, double-decker, jitney, motorbus, motorcoach, omnibus, passenger vehicle',
               'buses',  'bushes',    'business card', 'business cards',    'butane gas cylinder',   'butcher shop',  'butchery',
               'butter', 'butter dish',   'butterfly', 'buttocks',  'button',    'button box',    'button panel',  'buttons',
               'buttons panel',  'buttress',  'buzzer',    'bycicle carriage',  'caar',  'cabbages',  'cabin', 'cabinet',
               'cabins', 'cable', 'cable car', 'cable railway', 'cables',    'cactus',    'cage',  'cages', 'cake mold', 'calculator',
               'calendar',   'call buttons',  'camcorder', 'camel', 'camels',    'camera, photographic camera',   'camouflage',
               'camping stove',  'can',   'can opener',    'can, tin, tin can', 'canal', 'candelabrum, candelabra',   'candies',
               'candle', 'candle, taper, wax light',  'candles',   'candlestick, candle holder',    'candy bag', 'candy bags',
               'candy track',    'candy, confect',    'cane',  'canes', 'canister, cannister, tin',  'canlendar', 'cannon',
               'canoe',  'canopy',    'canvas',    'canvases',  'canyon',    'canyons',   'cap',   'cape',  'capital',   'caps',
               'car scrapping',  'car wash',  'car wreck', 'car, auto, automobile, machine, motorcar',  'caravan',   'caravans',
               'card',   'card display',  'card table',    'cardboard', 'cards', 'cargo', 'carousel',  'carousel horse',    'carp',
               'carpets',    'carport',   'carriage',  'cars scraping', 'cars scrapping',    'cart',  'carts',
               'case, display case, showcase, vitrine',  'cases', 'cash register, register',   'casing',    'casing interior',
               'casket', 'casserole', 'cassette',  'cassettes', 'castle',    'cat',   'catch', 'catwalk',   'cauldron',  'cave',
               'cave entrance',  'cavern',    'cd',    'cd box',    'cd player', 'cd rack',   'cd shelf',  'cd stack',  'cd stand',
               'cds',    'cds box',   'ceiing',    'ceiling',   'ceiling controls',  'ceiling decor', 'ceiling piece',
               'ceiling recessed light', 'cell',  'cell door', 'cello', 'cello cover',   'cells',
               'cellular telephone, cellular phone, cellphone, cell, mobile phone',  'cement',    'centerpiece',
               'central processing unit, CPU, C P U , central processor, processor, mainframe',  'central reservation',
               'centrifuge', 'ceramic box',   'ceramic pot',   'ceramic ware',  'ceramics box',  'certificate',   'chain', 'chains',
               'chainsaw',   'chair', 'chair desk',    'chair lift',    'chairs desk',   'chairs lift',   'chaise lounge', 'chalk',
               'champagne bucket',   'champagne stand',   'chandelier, pendant, pendent',  'change machine',    'check-in-desk',
               'check-in-desks', 'checkers pieces',   'checkers table',    'checkpoint',    'cheese',    'cheese dish',   'chess',
               'chest',  'chest of drawers, chest, bureau, dresser',  'chick', 'chicken',   'chicks',    'chimney',   'chimneys',
               'chinese lantern',    'chip',  'chippings', 'chips', 'chocolate', 'chocolates',    'chopping board, cutting board',
               'chopstick',  'chorizo',   'chorizos',  'christmas lights',  'christmas tree',    'church',    'chute', 'cigar box',
               'cigarette',  'cigarette packet',  'cigarettes',    'ciment mixer',  'circular saw',  'circus',    'cistern',
               'cistern, water tank',    'city',  'clamp', 'clamp lamp',    'clams', 'cliff, drop, drop-off', 'cliffs',
               'climbing frame', 'clip',  'clipboard', 'cloak', 'clock', 'clock face',    'clock radio',   'closet',    'closet rod',
               'closure',    'cloth material',    'clothes hanging',   'clothes horse', 'clothes stand', 'clothespin',
               'clothing',   'clothing rack', 'cloud', 'clouds',    'club',  'clubs', 'clutch pedal',  'coar of arms',  'coaster',
               'coasters',   'coastline', 'coat',  'coat of arms',  'coat rack', 'coat stand',    'coats', 'cobbles',   'cock',
               'cockpit',    'cockpot',   'cocktail shaker',   'coconut',   'coconuts',  'coffee',    'coffee cup',    'coffee cup rack',
               'coffee cups',    'coffee grinder',    'coffee maker',  'coffee pot',    'coffee table, cocktail table',  'coffin',
               'colander',   'cold storage',  'cold storage door', 'cold store',    'colour board',  'columbarium',   'columbarium niche',
               'column', 'column, pillar',    'columns',   'comb',  'comforter', 'comic strip',   'compact discs', 'compartment',
               'compas', 'computer case', 'computer console',
               'computer, computing machine, computing device, data processor, electronic computer, information processing system',
               'confessional booth', 'console',   'console table, console',    'construction equipment',    'contact lens case',
               'container',  'containers',    'contrabass',    'control',   'control cabinet',   'control panel',
               'control panel, instrument panel, control board, board, panel',   'control panels',    'control room',
               'control table',  'control tower', 'controls',  'conveyer belt, conveyor belt, conveyer, conveyor, transporter',
               'cooker', 'cookie',    'cookies',   'cool box',  'cooler',    'coop',  'copier',    'coral', 'cord',  'cords', 'cork',
               'cork stopper',   'corkscrew', 'corn field',    'corner',    'corner pocket', 'cornice',   'counter',   'counters',
               'countertop', 'counterweight', 'court', 'courts',    'cove',  'cover', 'cover curtain', 'covered bridge',
               'covered wagon',  'cow, moo-cow',  'cowbell',   'cows',  'crackers',  'cradle',    'crane', 'crane scrapping',
               'crane truck',    'cranes',    'crank', 'craps table',   'crate', 'crater',    'crates',    'cream', 'cream tube',
               'creamer',    'creeper',   'crevasse',  'crib',  'crock', 'crock pot', 'crock rack',    'crockery',  'cross', 'cross bracing',
               'crosses',    'crosswalk', 'cruet', 'cruet set', 'crumb', 'crutch',    'cube',  'cubicles',  'cue',   'cue place',
               'cue rack',   'cue, cue stick, pool cue, pool stick',  'cues',  'cup',   'cup maker', 'cups',  'curb',  'curb cut',
               'curb, curbing, kerb',    'curbstone', 'curtain',   'curtain cover', 'curtain support',
               'curtain, drape, drapery, mantle, pall',  'curtains',  'cushion',   'cushions',  'cut slices machine',
               'cut table',  'cutlery',   'cutter',    'cyclotron', 'cylinder',  'cymbal',    'dam',   'dartboard', 'dashboard',
               'decanter',   'deck',  'deck boat', 'deck chair, beach chair',   'deck chairs',   'deck house',    'decoder',
               'decor',  'decoration, ornament, ornamentation',   'decorations',   'decorative glass',  'decorative wood',
               'deer',   'deer antler',   'deer head', 'deer skull',    'degree certificate',    'dental chair',
               'dental instruments', 'dental sink',   'dental swivel chair',   'deodorant', 'desert',    'desk',  'desk chair',
               'desk mat',   'desk organizer',    'detergent dispenser',   'developing machine',    'dial',  'dice',  'diffuser',
               'diffusor',   'digger',    'digital clock', 'diploma',   'dipper',    'dirt track',    'dish drainer',  'dish rack',
               'dish soap',  'dish towel',    'dish, dish aerial, dish antenna, saucer',   'dishcloths',    'dishes',
               'dishrag, dishcloth', 'dishwasher, dish washer, dishwashing machine',  'disk',  'disk spindle',  'disks',
               'dispenser',  'display',   'display board', 'display window, shop window, shopwindow, show window',
               'display, video display', 'disposal plant',    'distaff',   'ditch', 'divider',   'diving board',  'docks',
               'document, written document, papers', 'dog bed',   'dog dish',  'dog, domestic dog, Canis familiaris',
               'doily',  'doll',  'dollhouse', 'dolmen',    'dolmens',   'dolphin',   'dome',  'donkey',    'door',  'door bars',
               'door frame', 'doorbell',  'doorframe, doorcase',   'doors', 'doorway arch',  'dormer',    'dormer, dormer window',
               'double door',    'drain', 'drain pipe',    'drain plug',    'drain vent',    'drapes',    'drawer',    'drawers',
               'drawing',    'drawing board', 'drawing table', 'drawing tables',    'drawings',  'dress, frock',  'dresses',
               'dressing screen',    'dressing table',    'dried herbs',   'drift ice', 'drill', 'drill rig', 'drilling equipment',
               'drinking fountain',  'driveway',  'dropper',   'dropper bottle',    'drum',  'drums', 'dry dock',  'dryer', 'duck',
               'duck shelter',   'ducks', 'dumbbell',  'dumbbells', 'dummy', 'dune',  'duster',    'dustpan',   'dvd',   'dvd box',
               'dvd boxes',  'dvd player',    'dvd players',   'dvds',  'dvds box',  'dvds rack', 'dye',   'ear',   'earmuffs',
               'earphones',  'earring',   'earrings',  'ears',  'earth', 'earth, ground', 'easel', 'eaves', 'egg',   'eggs',
               'eiderdown, duvet, continental quilt',    'electrical device', 'electrical substation', 'electricity box',
               'electricity meter',  'electronic organ',  'elephant',  'elevator',  'elevator door', 'elevator doors',
               'elevator, lift', 'elliptical machine',    'embankment',    'ember', 'embrasure', 'engine',    'entrance',
               'entrance parking',   'entrance, entranceway, entryway, entry, entree',    'entry phone',   'envelope',
               'envelopes',  'eplant',    'equestrian obstacle',   'equipment', 'escalator, moving staircase, moving stairway',
               'escarpment', 'estuary',   'excavator', 'exercise bench',    'exercise bike', 'exercise bikes',
               'exercise machines',  'exhaust pipe',  'exhibitor', 'expedition',    'extension cord',    'external driver',
               'external drivers',   'extractor fan', 'extractor pipe',    'eye',   'eyebrow',   'eyeglasses',    'fabric',
               'fabric softener',    'fabric, cloth, material, textile',  'face',  'factory',   'fairground',
               'fairground ride',    'fan',   'faucet',    'faucet drain lever',    'faucet, spigot',    'fax',   'fax machine',
               'feather',    'feeder',    'feeding bottle',    'feeding trough',    'fence', 'fence post',    'fence rubble',
               'fence, fencing', 'fences',    'fender',    'fenders',   'fern',  'ferris wheel',  'field', 'field desert',
               'field flowers',  'field grass',   'figure',    'figurine, statuette',   'file',  'file box',  'file boxes',
               'file cabinet',   'file cabinets', 'file organizer',    'file, file cabinet, filing cabinet',    'files',
               'filing cabinets',    'filter',    'finger',    'finial',    'fire',  'fire alarm',    'fire alarm box',
               'fire bell',  'fire blanket',  'fire booth',    'fire engine',   'fire escape',
               'fire extinguisher, extinguisher, asphyxiator',   'fire hose', 'fire utensils', 'fireplace utensils',
               'fireplace, hearth, open fireplace',  'fireplug, fire hydrant, plug',  'firewood',  'fireworks', 'first floor',
               'fish',   'fish farm water',   'fish structure',    'fish tank', 'fishing pole',  'fitting room',  'flag',
               'flag pole',  'flags', 'flagstones',    'flame', 'flashlight',    'flask', 'flavorings',    'flight deck',
               'flip flop',  'flip flops',    'float', 'floatation device', 'floating bridge',   'floating dock', 'flock of sheep',
               'floodlight', 'floodlights',   'floor', 'floor light',   'floor recessed light',  'floor spotlight',
               'floor, flooring',    'floting dock',  'flower',    'flowerpots',    'flowers',   'fluorescent',
               'fluorescent, fluorescent fixture',   'flusher',   'flute', 'flyer', 'flyers',    'flyscreen', 'foam',  'fog',
               'fog bank',   'folded box',    'folders',   'folding chair', 'folding chairs',    'folding door',  'folding doors',
               'folding screen', 'folding table', 'font',  'food cart', 'food processor',    'food, solid food',  'foodstuffs',
               'foot',   'foot rail', 'foot rest', 'football',  'football boots',    'football stadium',  'football table',
               'football trophy',    'footboard', 'footbridge, overcrossing, pedestrian bridge',   'footpath',  'footrest',
               'forecourt',  'forest',    'forge', 'fork',  'forklift',  'forks', 'fort',  'fountain',  'frame', 'frames',
               'freezer',    'freezing ground',   'freight goods', 'freight train', 'fringe',    'front', 'front, front end, forepart',
               'fruit',  'fruit bowl',    'fruit machine', 'fruit stand',   'fryer', 'fryer basket',  'frying pan',
               'frying pans',    'fuel can',  'fuel pump', 'fuel tank', 'funfair',   'funicular', 'funnel',    'fur',   'furnace',
               'furnace room',   'furrow',    'fuselage',  'gable', 'game',  'game table',    'games', 'games room',
               'games table',    'gaming table',  'gangway',   'gap',   'garage',    'garage door',   'garage doors',  'garbage',
               'garden', 'garland',   'garlic',    'garlic cloves', 'garlics',   'garment bag',   'gas bottle',    'gas cap',
               'gas cylinder',   'gas heater',    'gas meter', 'gas pedal', 'gas pump',  'gas station',   'gas well',  'gasworks',
               'gate',   'gatehouse', 'gates', 'gateway',   'gauge', 'gaze',  'gazebo',    'gear',  'gear shift',    'gear wheel',
               'gears',  'gearshift', 'generator', 'girder',    'glacier',   'glass box', 'glass separation',  'glass, drinking glass',
               'glasses case',   'glove', 'glove compartment', 'gloves',    'goal',  'goat',  'goblet',    'goggles',   'goldfish bowl',
               'golf bag',   'golf ball', 'golf cart', 'golf club', 'golf green',    'goods', 'goose', 'gooses',    'gourd',
               'gramophone', 'grand', 'grand piano, grand',    'grandfather clock', 'grandstand, covered stand', 'grandstands',
               'grapevine',  'graphic equalizer', 'grass', 'grassland', 'grate', 'grater',    'grating',   'gravel',
               'gravestone, headstone, tombstone',   'gravestones',   'gravy boat',    'green light',   'greenhouse',
               'grid',   'griddle',   'grill', 'grill, grille, grillwork',  'grille',    'grille door',   'grills',    'grinder',
               'gripper',    'ground',    'ground desert', 'ground shrubs', 'guard rail',    'guardhouse',    'guillotine',
               'guitar', 'guitar case',   'guitar cover',  'gull',  'gun',   'gutter',    'gym machine',   'gym shoe, sneaker, tennis shoe',
               'h-stretcher',    'hair',  'hair dryer',    'hair spray',    'hairbrush', 'hairdresser chair', 'hairdressers chair',
               'hairpieces', 'half globe',    'half moon', 'hall',  'ham',   'hammer',    'hammock',   'hams',  'hand',  'hand bellows',
               'hand dryer', 'hand trolley',  'handbag',   'handcart, pushcart, cart, go-cart', 'handle',    'handle, grip, handgrip, hold',
               'handlebar',  'handrail',  'hands', 'hangar',    'hanger',    'hanger hook',   'hangers',   'hanging clothes',
               'hanging instrument', 'hanging utensils',  'harbor',    'hard drive',    'hardware',  'harness',   'harp',
               'hat, chapeau, lid',  'hatch', 'hatchery',  'hats',  'haversack', 'hay',   'hay bale',  'hay rolls', 'hay stacks',
               'head',   'head deer', 'head jamb', 'head rail', 'head sport',    'head, caput',   'headboard', 'headlight',
               'headlight, headlamp',    'headphones',    'headrest',  'headstone cross',   'headstones',    'hear',  'heart', 'hearth',
               'heated swimming pool',   'heater, warmer',    'heating',   'hedge partial', 'hedge, hedgerow',   'heel',  'heeled shoe',
               'helicopter', 'heliport',  'helmet',    'hen, biddy',    'henhouse',  'hens',  'herb',  'high-heeled shoe',
               'high-heeled shoes',  'highlight', 'highway bridge',    'hill',  'hill grass',    'hill leaves',   'hill pass',
               'hill urban', 'hills', 'hillside',  'hinge', 'hinge, flexible joint', 'hip tiles', 'hippopotamus head', 'hoarding',
               'hobby-elephant', 'hobby-horse',   'hockey table',  'hoist', 'hole',  'hole puncher',  'hollow',    'hood',
               'hood, exhaust hood', 'hoof',  'hook',  'hoop',  'horizontal bar',    'horse carousel',    'horse, Equus caballus',
               'hose',   'hosepipe',  'hot air balloon',   'hot mitt',  'hot peppers',   'hot tub',   'hotel safe',    'hotplate',
               'hourglass',  'house', 'house number',  'houseboat', 'housing',   'housing lamp',  'housing project',
               'hovel, hut, hutch, shack, shanty',   'howdah',    'hull',  'hutch', 'huts',  'ice bar',   'ice bucket',
               'ice cone',   'ice cream', 'ice cream machine', 'ice creme stand',   'ice decoration',    'ice field',
               'ice floe, floe', 'ice ground',    'ice hockey rink',   'ice lands', 'ice maker', 'ice mountain',  'ice rink',
               'ice shelf',  'ice wall',  'ice, water ice',    'iceberg',   'icicle',    'icicles',   'id card',   'idol',
               'igloo',  'in box',    'incense',   'incinerator',   'incubator', 'index card',    'index cards',   'indoor track',
               'industrial machine', 'industrial plant',  'industrial robot',  'industry',  'inflatable bounce game',
               'inflatable doll',    'inflatable glove',  'inflatable park',   'inflatable train',  'ingot, metal bar, block of metal',
               'inner square',   'inside arm',    'instrument',    'instrument control',    'instrument panel',  'instrument table',
               'instruments table',  'intercom',  'interior casing',   'ipod',  'iron',  'iron bar',  'iron cross',    'iron tubes',
               'ironing board',  'island',    'iv bag',    'jack',  'jacket',    'jam',   'jamb',  'jar',   'jars',  'jersey, T-shirt, tee shirt',
               'jetty',  'jewelry display',   'joist', 'joists',    'joystick',  'judge table',   'jug',   'juice machine',
               'juke box',   'junk',  'junk pile', 'kasbah',    'kayak', 'kennel',    'kennels',   'kettle, boiler',    'key',
               'key pad',    'keyboard',  'keys',  'killer whale',  'kit',   'kitchen island',    'kitchen towel', 'kitchen utensils',
               'kite',   'knife', 'knife display', 'knob',  'knobs', 'knocker',   'lab bench', 'label', 'label tag', 'label, recording label',
               'laboratory equipment',   'laboratory machine',    'laboratory machines',   'labyrinth', 'ladder',    'ladle',
               'lake',   'laminating machine',    'lamp',  'lamp cord', 'lamp housing',  'lamps', 'lampshade', 'lance', 'land, ground, soil',
               'landfill',   'landing gear',  'lantern',   'lanterns',  'laptop bag',    'laptop, laptop computer',   'large fork',
               'large rabbit',   'latch', 'lathe', 'lattice',   'laundry',   'laundry basket',    'lava',  'lawn',  'lawn mower',
               'leaf',   'leaf, leafage, foliage',    'leash', 'leather',   'leathers',  'leave', 'leaves',    'lectern',   'ledge',
               'ledges', 'left arm',  'left foot', 'left hand', 'left leg',  'left shoulder', 'leg',   'legs',  'lemon', 'letter mail',
               'level',  'lever', 'license plate', 'license plate, numberplate',    'lid',   'life preserver',    'light',
               'light bulb', 'light bulb, lightbulb, bulb, incandescent lamp, electric light, electric-light bulb',
               'light display',  'light pole',    'light source',  'light switches',    'light tower',   'light, light source',
               'lighter',    'lighting',  'lights',    'lily pads', 'linens',    'lithograph',    'litter basket', 'livestock',
               'loaves', 'lock',  'locker',    'lockers',   'lockgate',  'locomotive',    'lodge', 'loft',  'log',   'log holder',
               'logo',   'logs',  'loom',  'loudspeaker',   'loudspeaker, speaker, speaker unit, loudspeaker system, speaker system',
               'lower deck', 'lower sash',    'luggage',   'luggage rack',  'lumber, timber',    'mace',  'machine',   'machine gun',
               'machinery',  'machines',  'magazine',  'magazine rack', 'magnet',    'mail boxes',    'mailboxes', 'make',  'makeup',
               'mallet', 'manchette', 'manhole',   'mannequin', 'manometer', 'mantle',    'mantle piece',  'map',   'maps',  'margarine',
               'marker', 'marquee',   'marsh water',   'mask',  'massage bed',   'massage table', 'mast',  'mat',   'material',
               'material rolls', 'materials', 'mattress',  'mausoleum', 'maze',  'measuring spoons',  'meat',  'meat bag',
               'meat bags',  'meat hooks',    'meat piece',    'meat pieces',   'mechanical shovel', 'mechanism', 'median',
               'medical machine',    'medicines', 'megaphone', 'menu',  'menu card', 'menu display',  'menus', 'merchandise, ware, product',
               'merry-go-round', 'mesh guard rail',   'message board', 'metal decoration',  'metal piping',  'metal profiles',
               'metal shutter',  'metal shutters',    'metal structure',   'meter', 'meter box', 'meters',    'mezzanine, first balcony',
               'microbrewery',   'microphone',    'microphone, mike',  'microscope',    'microwave, microwave oven', 'milestone',
               'milk jug',   'mill',  'millrace',  'minar', 'minaret',   'minced meat',   'mine',  'mineral',   'miniature chair',
               'miniature sofa', 'minibike, motorbike',   'mirror',    'mirror support',    'mirrors',   'missile',   'mitra',
               'mitten', 'mixer', 'mixing board',  'mobile',    'mobile conveyor',   'mobile home',   'mobile phone',  'model',
               'model dinosaur', 'models',    'mold',  'molding',   'money', 'monitor',   'monitor, monitoring device',    'monitors',
               'monkey', 'monolith',  'monument',  'moon',  'moon decoration',   'moon dial', 'moose', 'mop',   'mop handle',
               'mortar', 'mosaic',    'mosque',    'moss',  'motion detector',   'motion sensor', 'motor', 'motorbike cart',
               'motorboat',  'motorboats',    'moulding',  'mound', 'mountain ledge',    'mountain pass', 'mountain salt',
               'mountain terraces',  'mountain, mount',   'mouse', 'mouse stand',   'mouse, computer mouse', 'mousepad, mouse mat',
               'mouth',  'movie poster',  'moving walkway',    'mudflat',   'mug',   'mug set',   'mugs',  'mulch', 'multiple plug',
               'multiple socket',    'muntin',    'munting',   'mural', 'mushroom',  'music box', 'music control table',
               'music devices',  'music machine', 'music stand',   'musical instruments',   'musicians place',   'mussels',
               'mustache',   'nail',  'nail brush',    'name plate',    'napkin holder', 'napkin rack',   'napkin ring',
               'napkin, table napkin, serviette',    'napkins',   'neck',  'necklace',  'necklace display',  'necklaces', 'necktie',
               'nest',   'net',   'netting',   'newspaper stand',   'newspaper, paper',  'newspapers',    'niche', 'night light',
               'nose',   'notbook',   'note',  'notebook',  'notecards', 'notepad',   'notes', 'notice',    'notice board',
               'nuclear reactor',    'numbers',   'numeral, number',   'nunchaku',  'nuts',  'oar',   'obelisk',   'observatory',
               'obstacle',   'odometer',  'office',    'office partition',  'office window', 'offices',   'oil',   'oil jar',
               'oil lamp',   'oil tube',  'oil tubes', 'oilcloth',  'onion', 'onions',    'opening',   'operation table',   'orange',
               'oranges',    'orchestra', 'organ', 'organizer', 'oriental lantern',  'ornament',  'ornamental box',
               'ornamental structure',   'ornaments', 'ottoman, pouf, pouffe, puff, hassock',  'outboard motor',    'outhouse',
               'outhouse wc',    'outlet',    'outside arm',   'oven',  'overflot plate',    'overhang',  'overpass',  'oxygen tank',
               'oyster bank',    'pack',  'pack bags', 'pack of cigarettes',    'pack of snuff', 'package',   'packages',  'packet',
               'packets',    'pad',   'pad of paper',  'paddle',    'padlock',   'page',  'pagoda',    'paint box', 'paint brush',
               'paint brushes',  'paint bucket',  'paint can', 'paint pot', 'paintbrush',    'painting, picture', 'paintings',
               'paints', 'palette',   'palisade',  'pallet',    'pallets',   'palm',  'palm trees',    'palm, palm tree',   'pan',
               'pane',   'pane, pane of glass, window glass', 'panel', 'panelling', 'panels',    'panes', 'pans',  'pantheon',
               'pantry', 'pants', 'paper', 'paper box', 'paper clip',    'paper cups',    'paper dishes',  'paper dispenser',
               'paper file', 'paper filer',   'paper napkin',  'paper napkins', 'paper rack',    'paper roll',    'paper rolls',
               'paper towel',    'paper towels dispenser',    'paper weight',  'paperpile', 'paperweight',   'park',  'park gear',
               'parking',    'parking entrance',  'parking lot',   'parking meter', 'parking place', 'parking space', 'parterre',
               'partition wall', 'partition, divider',    'pastries',  'pastry',    'patches',   'path',  'patio', 'patio, terrace',
               'patty, cake',    'pavilion',  'pavilions', 'paving',    'paving stone',  'peach', 'peak',  'peaked cap',
               'peaks',  'pebbles',   'pectoral machine',  'pedal', 'pedal boat',    'pedestal',  'pedestal, plinth, footstall',
               'pediment',   'pelota court',  'pelt',  'pelts', 'pen',   'pen box',   'pen holder',    'pen set',   'pencil',
               'pencil case',    'pencil cup',    'pencil sharpener',  'pencils',   'pendant',   'pendant lamp',  'pendulum',
               'penguin',    'pens',  'pepper',    'pepper grinder',    'pepper shaker', 'peppers',   'pergola',   'person',
               'person walking', 'person, individual, someone, somebody, mortal, soul',   'pestle',    'pet bowl',  'pet dish',
               'petal',  'petrol pump',   'petrol pump hose',  'petrol pumps',  'petrol station',    'phone charger', 'phone fax',
               'phone jack', 'photo', 'photo album',   'photo backdrops',   'photo machine', 'photocopier',   'piano pedals',
               'piano, pianoforte, forte-piano', 'pick',  'picnic spot',   'pictures',  'pie',   'pie spinach',   'piece', 'pieces',
               'pier',   'pier, wharf, wharfage, dock',   'pig',   'pig statue',    'pig tail',  'pigeon',    'pigeonhole',
               'pigsty', 'pile of junk',  'pile of trash', 'pillar',    'pillars',   'pillow',    'pillows',   'pilon', 'pilot cockpit',
               'pinball',    'pine cone', 'pine decor',    'pine decoration',   'pineapple', 'pinecone',  'pinecones', 'ping pong paddle',
               'pins',   'pipe',  'pipe drain',    'pipe, pipage, piping',  'pipe, tube',    'piper', 'pipette',   'piping',
               'piston', 'pit',   'pitch', 'pitcher, ewer', 'pitchfork', 'placard',   'place card',    'place mat', 'place mats',
               'place setting',  'placecard', 'placecard holder',  'plain', 'plane', 'planer',    'planetarium',   'planks',
               'plant',  'plant box', 'plant pots',    'plant stand',   'plant, flora, plant life',  'planter',   'plants',
               'plants pot', 'plaque',    'plastic',   'plastic cup',   'plastic cups',  'plastic sheet', 'plate', 'plate mat',
               'plate rack', 'plateau',   'plates rack',   'platform',  'plats', 'platter',   'playground',    'playground equipment',
               'playpen',    'plaything, toy',    'pliers',    'plinth',    'plug',  'podium',    'poker', 'pole',  'pole sign',
               'poles',  'polythene cover',   'poncho',    'pond',  'pond water',    'pool',  'pool ball', 'pool balls',
               'pool bar',   'pool bass', 'pool table, billiard table, snooker table', 'pool triangle', 'popcorn machine',
               'porch',  'porch rail',    'porexpan board',    'port',  'portable fridge',   'portfolio', 'post',  'post box',
               'post light', 'post-it',   'postal card',   'postbox',   'postbox, mailbox, letter box',  'postcard',  'postcard display',
               'postcard stand', 'postcards', 'poster board',  'poster, posting, placard, notice, bill, card',  'posters',
               'posters pole',   'postes',    'posts', 'pot',   'pot hanger',    'pot holder',    'pot lid',   'pot of herbs',
               'pot pen',    'pot rack',  'pot, flowerpot',    'potatoes',  'pots',  'potted fern',   'potters wheel',
               'pottery, clayware',  'powder',    'powder compact',    'power', 'power box', 'power cord',    'power line',
               'power lines',    'power meter',   'power outlet',  'power point',   'power strip',   'precipice',
               'precision balance',  'press', 'pressure cooker',   'pressure gauge',    'pressure washer',   'price list',
               'price tag',  'printed matter',    'printer',   'private place', 'processing machine',    'production line',
               'professional degree',    'projector', 'projector rack',    'propeller', 'propellers',    'pub front', 'puddle',
               'pulley', 'pulpit',    'pumpkin',   'pumpkins',  'punching bag',  'puppet',    'purses',    'push button, push, button',
               'push buttons',   'pyjamas',   'pylon, power pylon',    'pyramid',   'quay',  'quicksand', 'quilt', 'quonset hut',
               'quonset huts',   'rabbit',    'rack',  'rack cue',  'rack tool', 'racket',    'rackets',   'racking chair', 'racks',
               'racquet',    'radar', 'radar screen',  'radiator',  'radio', 'radiography',   'raft',  'rafting',   'rail',  'railing',
               'railing, rail',  'railings',  'railroad',  'railroad track',    'railroad tracks',   'railroad train',
               'rails',  'railway',   'railway engine',    'railway tie',   'railway yard',  'railways',  'rain drain',
               'rain gutter',    'rain pipe', 'rainbow',   'rainshield',    'rake',  'rakes', 'ramp',  'ranch', 'raw disposal basket',
               'ray',    'razor', 'razor cut hair',    'reaper',    'rear dash', 'receiver',  'recessed light',    'reclining chair',
               'record player',  'recorder',  'records',   'recycling bin', 'recycling materials',   'recycling plant',
               'recycling trash',    'red board', 'red light', 'reed',  'reel',  'reels', 'refinery',  'refrigerator, icebox',
               'refuge', 'remains',   'remote control, remote',    'rescue float',  'rest',  'restroom',  'revolving door',
               'revolving doors',    'revolving pass',    'ribbon',    'ribbons',   'ride',  'ride structure',    'ride tiles',
               'rider',  'ridge', 'ridge liles',   'ridge tiles',   'rifle', 'rifles',    'right arm', 'right foot',
               'right hand', 'right leg', 'right shoulder',    'rim',   'ring',  'ring bell', 'ring binder',   'rings', 'riser',
               'river',  'river bank',    'road',  'road, route',   'roadroller',    'roads', 'roasting',  'rock',  'rock formations',
               'rock wall',  'rock, stone',   'rocker',    'rocket',    'rocking',   'rocking chair', 'rocking horse', 'rocks',
               'rocky formation',    'rocky formations',  'rocky wall',    'rod',   'roll',  'roller',    'roller coaster',
               'roller coaster cars',    'rolling mill',  'rolls', 'roof',  'roof rack', 'root',  'roots', 'rop',   'rope',
               'rope bridge',    'ropes', 'rose',  'rose window',   'rotisserie',    'roulette',  'roulette table',    'roundabout',
               'router', 'rowing boat',   'rowing machine',    'rubber glove',  'rubber ring',   'rubbish',   'rubbish, trash, scrap',
               'rubble', 'rudder',    'rug, carpet, carpeting',    'ruins', 'rule',  'rung',  'runnel water',  'runner',
               'runner cloth',   'runway',    'runway strip',  'sack',  'sacks', 'sacks wall',    'saddle',    'safe',  'safe door',
               'safes',  'safety belt',   'safety net',    'safety rail',   'safety side',   'safety suit',   'sail',  'sailboat',
               'sailing boat',   'saline solution',   'salt',  'salt and pepper',   'salt and pepper shakers',   'salt marsh',
               'salt pepper cellar', 'salt plain',    'salt shaker',   'saltcellar',    'sanck bar', 'sand',  'sand dune', 'sand dunes',
               'sand hill',  'sand track',    'sand trap', 'sandal',    'sandbar',   'sandbox',   'sandpit',   'sandwich',  'santa claus',
               'sash',   'sash lock', 'satellite turner',  'sauce', 'saucepan',  'saucepans', 'saucers',   'sauna', 'savanna',
               'saw',    'sawhorse',  'scaffolding, staging',  'scale, weighing machine',   'scanner',   'scarecrows',    'scarf',
               'scarfs', 'schoolyard',    'scissors',  'sconce',    'scoop', 'score', 'scoreboard',    'scotch tape',   'scourer',
               'scratching post',    'screen',    'screen door, screen',   'screen stand',  'screen, CRT screen',
               'screen, silver screen, projection screen',   'screens',   'screw', 'screwdriver',   'screwdrivers',  'screws box',
               'scrub',  'scrubland', 'sculpture', 'sculptures',    'sea',   'sea star',  'sea water ice', 'seagull',   'seal',
               'sealing roll',   'sealing tape',  'seaplane',  'seat',  'seat base', 'seat belt', 'seat belt clipper', 'seat cushion',
               'seat water', 'seating',   'seats', 'secateurs', 'secretary table',   'security camera',   'security cameras',
               'security checkpoint',    'security cordon',   'security door', 'security door frame',   'security light',
               'seedbed',    'seesaw',    'segment',   'seltzer bottle',    'semi-flush mount lights',   'semidesert ground',
               'sensor', 'sepulcher', 'server',    'servers',   'service elevator',  'service station',   'set of instruments',
               'set of pigeonholes', 'set office',    'set square',    'sewer', 'sewer cover',   'sewer drain',   'sewing box',
               'sewing machine', 'shack', 'shade', 'shaft', 'shaker',    'shampoo',   'shanties',  'shanty',    'shantytown',
               'shape',  'shark', 'shaving brush', 'shavings',  'shawl', 'shed',  'sheep', 'sheep pen', 'sheeps',    'sheet',
               'sheets', 'shelf', 'shell', 'shell, case, casing',   'shellfish', 'shells',    'shelter',   'shelves',   'shield',
               'ship',   'shipyard',  'shirt', 'shoal', 'shoe',  'shoe rack', 'shoelace',  'shoji screen',  'shooting pad',
               'shop window',    'shop, store',   'shopping bag',  'shopping cart', 'shopping carts',    'shops', 'shore', 'shorts',
               'shoulder',   'shovel',    'shower',    'shower curtain',    'shower door',   'shower faucet', 'shower room',
               'shower shelf',   'shower stall, shower bath', 'shower tray',   'showerhead',    'showers',   'shrine',    'shrub',
               'shrub, bush',    'shrubbery', 'shutter',   'shutters',  'side',  'side jamb', 'side pocket',   'side rail',
               'sidewalk',   'sidewalk, pavement',    'sieve', 'sign',  'signboard, sign',   'sill',  'silo',  'silos',
               'silver bird statue', 'silver canister',   'silverware',    'single hung',   'sink',  'sinkhole',  'sinkhole water',
               'sinks',  'site hut',  'skate', 'skateboard',    'skates',    'skating boots', 'skating rink',  'skeleton',
               'sketch', 'ski',   'ski lift',  'ski lift cabin',    'ski lift pole', 'ski pole',  'ski slope', 'ski stand',
               'ski trail',  'skids', 'skimmer',   'skip',  'skirt', 'skirting board',    'skirts',    'skis',  'skittle',
               'skittle alley',  'skittles',  'skull', 'skulls',    'sky',   'skylight',  'skylight, fanlight',    'skyscraper',
               'skyscrapers',    'skywalk',   'slat',  'slates',    'slats', 'sled',  'sledgehammer',  'sleeping bag',  'sleeping robe',
               'sleigh', 'slice', 'slicer',    'slide', 'slides',    'sliding',   'sliding door',  'slipper',   'slippers',  'slope',
               'slot machine, coin machine', 'slotted spoon', 'slow cooker',   'slum shanties', 'small chair',   'small table',
               'smoke',  'smoke detector',    'smoke escape',  'snacks',    'sneakers',  'snow',  'snowboard', 'snowboard shape',
               'snowboarder',    'snowshoe',  'snowy', 'snowy mountain pass',   'snuffs',    'soap',  'soap bar',  'soap dish',
               'soap dispenser', 'soaps', 'soccer ball',   'sock',  'socket',    'sockets',   'socks', 'sofa bed',
               'sofa, couch, lounge',    'soil',  'solar energy',  'solar panel',   'solar panels',  'solt machine',
               'sopping cart',   'souk',  'sound equipment',   'spade', 'spanner',   'spanners',  'spatula',   'spatulas',
               'speaker',    'special shape', 'spectacle-case',    'spectacles, specs, eyeglasses, glasses',    'sphere',
               'spice',  'spice jar', 'spice rack',    'spices',    'spices rack',   'spillway',  'spinach',   'spindle',
               'sping',  'spiral staircase',  'spire', 'sponge',    'sponges',   'spoon', 'spoons',    'sport bag', 'sports bag',
               'spotlight, spot',    'spotlights',    'spout', 'spray', 'spray bottle',  'spray can', 'sprays',    'spread',
               'sprinkler',  'square',    'squash',    'squeezer',  'squirrel',  'ssign', 'stabilizer',    'stables',   'stadium',
               'stage',  'stained glass', 'stained-glass window',  'staircase', 'stairs, steps', 'stairway, staircase',   'stake',
               'stalactite', 'stalactites',   'stalagmite',    'stalagmites',   'stall, stand, sales booth', 'stalls',    'stands',
               'stapler',    'star',  'starfish',  'starting gate', 'starting gate trolley', 'station',   'stationary bicycle',
               'statue', 'statue piller', 'statues',   'stave', 'steam roller',  'steam room',    'steam shovel',  'steam vase',
               'steamroller',    'steel', 'steel beam',    'steel box', 'steel chair',   'steel industry',    'steel wire',
               'steeple',    'steering',  'steering wheel',    'steering wheel, wheel', 'stem',  'step',  'step machine',
               'step, stair',    'steps', 'steps machine', 'stereo',    'stethoscope',   'stick', 'sticker',   'sticks',
               'sticky tape dispenser',  'stile', 'stilt', 'stocking',  'stockings', 'stone', 'stone ball',    'stone path',
               'stone slab', 'stool', 'stools',    'stopper',   'storage',   'storage box',   'storage jar',   'storage rack',
               'store',  'storm drain',   'storm grate',   'storm sewer',
               'stove',  'stove, kitchen stove, range, kitchen range, cooking stove', 'strainer',  'straw', 'straw bale',
               'straw bales',    'strawberries',  'strawberry',    'straws',    'stream',    'street box',    'street grate',
               'street lights',  'street market', 'street name',   'street number', 'street sign',   'street wires',
               'streetcar, tram, tramcar, trolley, trolley car', 'streetlight, street lamp',  'stretcher', 'string',
               'stringer',   'strip light',   'stripe',    'stripes',   'strips',    'strongbox', 'strongroom',    'structure',
               'stuffed animal', 'stuffed animal head',   'stuffed head',  'stump', 'stumps',    'sty',   'submarine', 'subway',
               'sugar',  'sugar bowl',    'sugar packet',  'suit',  'suit hanger',   'sulfur mine',   'sun',   'sun deck',
               'sun room',   'sunflower', 'sunflower field',   'sunglasses',    'supermarket',   'supplies',  'support',
               'support beam',   'support pole',  'supporting iron metal', 'supporting metal',  'surfboard', 'suspenders',
               'suspension rope bridge', 'suspensions',   'sutter',    'swamp', 'sweater',   'sweater, jumper',   'sweatshirt',
               'sweatshirts',    'sweep', 'sweet peas',    'swimming costume',  'swimming pool ladder',
               'swimming pool, swimming bath, natatorium',   'swimsuit',  'swing', 'swinging seat', 'swings',    'swiss chard',
               'switch', 'switch box',    'switch, electric switch, electrical switch',    'switchboard',   'switches',
               'swivel chair',   'swmming pool',  'sword', 'synthesizer',   'system',    'table', 'table base',    'table cloth',
               'table football', 'table game',    'table mat', 'table runner',  'table runners', 'table tennis',  'tablecloth',
               'tablecloths',    'tableland', 'tables',    'tag',   'tail',  'tailight',  'taillight', 'tallboy',   'tank lid',
               'tank top',   'tank, storage tank',    'tanker',    'tanker aircraft',   'tanks', 'tap',   'tap wrench',    'tape',
               'tape measure',   'taper', 'tapes', 'tapestry, tapis',   'target',    'tarmac',    'tarp',  'tarpaulin', 'tart',
               'tassle', 'tea set',   'teacup',    'teapot',    'teeth', 'telegraph pole',    'telephone',
               'telephone booth, phone booth, call box, telephone box, telephone kiosk', 'telephone directories',
               'telephone pole', 'telephone, phone, telephone set',   'telescope', 'television camera',
               'television receiver, television, television set, tv, tv set, idiot box, boob tube, telly, goggle box',
               'television stand',   'temple',    'tennis court',  'tennis racket', 'tennis table',  'tent, collapsible shelter',
               'tents',  'terminal',  'terrace',   'terrace cafe',  'terraces',  'test',  'test tube', 'test tubes',
               'text, textual matter',   'textile loom',  'textile mill',  'textiles',  'thermometer',   'thermos',   'thermostat',
               'thread', 'threads',   'threshold', 'throne',    'throw', 'ticket box',    'ticket counter',    'ticket machine',
               'ticket office',  'ticket vending machine',    'ticket window', 'tie',   'ties',  'tiger', 'tile',  'tiles', 'till',
               'tilt wand',  'tin box',   'tins',  'tinsel',    'tire',  'tire seat', 'tires', 'tissue',    'tissue dispenser',
               'tissues',    'toaster',   'toaster oven',  'toe board', 'toilet bag',    'toilet brush',  'toilet kit',
               'toilet paper holder',    'toilet paper roll', 'toilet paper rolls',    'toilet set',
               'toilet tissue, toilet paper, bathroom tissue',   'toilet, can, commode, crapper, pot, potty, stool, throne',
               'toilete kit',    'toll booth',    'toll gate', 'toll plaza',    'tomato',    'tomatoes',  'tomb',  'tombs',
               'tombstones', 'tongs', 'tongue',    'tool',  'tool kit',  'toolbox',   'tools', 'tools box', 'tooth cleaner',
               'toothbrush', 'toothpaste',    'toothpick', 'top',   'top support',   'tops',  'torch', 'tornado',   'torrent water',
               'torso',  'towel', 'towel dispenser',   'towel paper',   'towel rack, towel horse',   'towel radiator',
               'towel rail', 'towel ring',    'tower', 'town',  'track', 'tracks',    'tractor',
               'trade name, brand name, brand, marque',  'traffic cone',  'traffic cones', 'traffic light, traffic signal, stoplight'
               'traffic marker', 'trailer',   'trailers',  'train, railroad train', 'training potty',    'trampoline',
               'tramway',    'transformer',   'trap door', 'trash bag', 'trash bags',    'trash trolley', 'travel bag',
               'tray',   'tray rack', 'tread', 'treadmill', 'treadmills',    'tree',  'trees', 'trellis',   'trench',    'trestle',
               'trestle bridge', 'trestles',  'tricycle',  'tripod',    'troller',   'troller bin',   'trolley basket',
               'trolley crane',  'trolley drawers',   'trolley table', 'trolley tools', 'trolley tray',  'trolleys',  'trolly',
               'trophies',   'trophy, prize', 'trough',    'trouser, pant', 'trowel',    'truck crane',   'truck, motortruck',
               'truckle bed',    'trucks',    'trumpet',   'trunk', 'trunk, tree trunk, bole',   'tube',  'tubes', 'tubing',
               'tumble dryer',   'tumble dryers', 'tundra',    'tunnel',    'turbine engine',    'tureen',    'turnbuckle',
               'turntables', 'turtle',    'twigs', 'twizzlers', 'typewriter',    'umbrella',  'umbrella rack', 'umbrella stand',
               'umbrellas',  'underground',   'underground station',   'undergrowth',   'underpass', 'units', 'upper', 'upper sash',
               'urbanization',   'urinal',    'urn',   'utensils',  'utensils canister', 'utensils rack', 'utility box',
               'utility cover',  'utility covers',    'utility panel', 'utility panels',    'vacuum cleaner',    'valance',
               'valley urban',   'valley, vale',  'valve', 'van',   'vane',  'vanity',    'vanity bag',    'vase',  'vases', 'vault',
               'vaulted niche',  'vegetables',    'veil',  'velodrome', 'vending machine',   'vent',
               'vent, venthole, vent-hole, blowhole',    'ventilation shaft', 'ventilator',    'veranda awning',
               'verandah',   'verge', 'vessel',    'vest',  'viaduct',   'video', 'video camera',  'video game',    'video-tape',
               'videocassette recorder, VCR',    'videos',    'viewpoint', 'village',   'vine',  'vine shoot',    'vinegar jar',
               'vinery', 'vineyard',  'vintage bottle filler', 'violin',    'violoncello',   'visit cards',   'visor', 'volcano',
               'volleyball court',   'voting booth',  'wafers',    'wagon', 'wagons',    'walker',    'walkie talkie',
               'walking stick',  'walkway',   'wall',  'wall clock',    'wall mount',    'wall recessed light',
               'wall socket, wall plug, electric outlet, electrical outlet, outlet, electric receptacle',    'wallet',
               'walrus', 'wardrobe, closet, press',   'warehouse', 'warship',   'washbasin chair',
               'washer, automatic washer, washing machine',  'washing hair',  'washing machines',  'watch', 'watchtower',
               'water',  'water bog', 'water chute',   'water cooler',  'water dispenser',   'water ditch',
               'water faucet, water tap, tap, hydrant',  'water filter',  'water hole',    'water lily',    'water machine',
               'water mill', 'water mist',    'water pump',    'water spurt',   'water surf',    'water tower',   'water valve',
               'water vapor',    'water wheel',   'watercraft',    'waterfall', 'waterfall, falls',  'watering can',  'waterscape',
               'waterway',   'wave',  'waves', 'way',   'weapon',    'weapons',   'weathervane',   'webcam',    'weeds', 'weighbridge',
               'weight', 'weights',   'welcome card',  'well',  'wheat', 'wheat field',   'wheel', 'wheelbarrow',   'wheelchair',
               'wheelhouse', 'wheels',    'whisk', 'whistle',   'white coat',    'white mark',    'wicker basket', 'wig',   'winch',
               'wind chimes',    'wind turbine',  'windmill, aerogenerator, wind generator',   'window',    'window frame',
               'window latch',   'window rose',   'window scarf',  'windowpane, window',    'windows',   'windshield',
               'windshield, windscreen', 'wine rack', 'wing',  'winglet',   'wipe',  'wiper', 'wipers',    'wire mesh', 'wire mower',
               'wire, conducting wire',  'wireless',  'wireless phone',    'wires', 'witness stand', 'wok',   'wood',  'wood art',
               'wood blocks',    'wood board',    'wood box',  'wood figure',   'woodcarving',   'wooden cutlery',    'wooden overhang',
               'wooden structure',   'wooden utensils',   'wooden wedge',  'work coat', 'work hut',  'work surface',  'workbench',
               'workstation',    'worktable, work table', 'wreath',    'wrenches',  'writing desk',  'x-rays',    'x-rays bed',
               'yellow light',   'yoke',  'ziggurat',  'zipper',    ', ', 'carapace, shell, cuticle, shield',  'jersey, t-shirt, tee shirt',
               'anchor, ground tackle',  'rocking chair, rocker', 'dog, domestic dog, canis familiaris',   'chest of drawers',
               'horse, equus caballus',  'altar, communion table, lord''s table', 'screen, crt screen',
               'andiron, firedog, dog, dog-iron',    'sailboat, sailing boat',    'pala',  'alarm, warning device, alarm system',
               'amphitheater, amphitheatre, coliseum',   'tarmacadam, tarmac, macadam',   'aquarium, fish tank, marine museum',
               'playing field, athletic field, playing area, field',
               'cash machine, cash dispenser, automated teller machine, automatic teller machine, automated teller, automatic teller, atm',
               'armor, armour',  'water vapor, water vapour', 'alarm clock, alarm',    'caca',
               'central processing unit, cpu, c p u , central processor, processor, mainframe',  'art, fine art',
               'ninepin, skittle, skittle pin',  'hai',   'card game, cards',  'altarpiece, reredos',
               'gas pump, gasoline pump, petrol pump, island dispenser', 'light switch',  'orifice, opening, porta',
               'seaplane, hydroplane',   'flood, floodlight, flood lamp, photoflood', 'microwave', 'screem',    'sled, sledge, sleigh',
               'toy',    'mug holder',    'aircraft carrier, carrier, flattop, attack aircraft carrier',   'videocassette recorder, vcr',
               'painiting',  'swab, swob, mop',   'adding machine, totalizer, totaliser',  'compueter', 'alga, algae',   'doble door',
               'radio receiver, receiving set, radio set, radio, tuner, wireless',   'autoclave, sterilizer, steriliser'];

labelTransferDict = {
    # ADE20K:                                               ygomi
    # 'static'
    'container':                                            'static',
    'ashcan, trash can, garbage can, wastebin, ash bin, ash-bin, ashbin, dustbin, trash barrel, trash bin': 'static',
    'flag':                                                 'static',
    # 'sky'
    'sky':                                                  'sky',
    # 'building'
    'balcony':                                              'building',
    'building, edifice':                                    'building',
    'barn':                                                 'building',
    'barrack buildings':                                    'building',
    'windowpane, window':                                   'building',
    'skyscraper':                                           'building',
    'pane, pane of glass, window glass':                    'building',
    'house':                                                'building',
    'gate':                                                 'building',
    'door':                                                 'building',
    'double door':                                          'building',
    'awning, sunshade, sunblind':                           'building',
    'bus station':                                          'building',
    'bus stop':                                             'building',
    'wall clock':                                           'building',
    'crane':                                                'building',
    # 'road'
    'road, route':                                          'road',
    'path':                                                 'road',
    'dirt track':                                           'road',
    # 'sidewalk'
    'sidewalk, pavement':                                   'sidewalk',
    # 'fence'
    'balustrade':                                           'fence',
    'railing, rail':                                        'fence',
    'fence, fencing':                                       'fence',
    'bannister, banister, balustrade, balusters, handrail': 'fence',
    # 'wall'
    'wall':                                                 'wall',
    'partition wall':                                       'wall',
    # 'curb'
    'curb':                                                 'curb',
    'curb cut':                                             'curb',
    'curb, curbing, kerb':                                  'curb',
    'curbstone':                                            'curb',
    # 'traffic sign'
    'street sign':                                          'traffic sign',
    'pole sign':                                            'traffic sign',
    'sign':                                                 'traffic sign',
    'signboard, sign':                                      'traffic sign',
    'bulletin board, notice board':                         'traffic sign',
    'text, textual matter':                                 'traffic sign',
    # 'traffic light'
    'traffic light, traffic signal, stoplight':             'traffic light',
    # 'pole'
    'streetlight, street lamp':                             'pole',
    'pole':                                                 'pole',
    'column, pillar':                                       'pole',
    'poles':                                                'pole',
    # 'terrain'
    'sand':                                                 'terrain',
    'land, ground, soil':                                   'terrain',
    'grass':                                                'terrain',
    'earth, ground':                                        'terrain',
    'central reservation':                                  'terrain',
    'field':                                                'terrain',
    # 'vegetation'
    'tree':                                                 'vegetation',
    'trees':                                                'vegetation',
    'shrub, bush':                                          'vegetation',
    'plant, flora, plant life':                             'vegetation',
    'palm, palm tree':                                      'vegetation',
    'mountain, mount':                                      'vegetation',
    'hill':                                                 'vegetation',
    'flower':                                               'vegetation',
    'bushes':                                               'vegetation',
    # 'bridge'
    'bridge, span':                                         'bridge',
    # 'car'
    'car, auto, automobile, machine, motorcar':             'car',
    # 'truck'
    'airport cart':                                         'truck',
    'truck, motortruck':                                    'truck',
    'bus, autobus, coach, charabanc, double-decker, jitney, motorbus, motorcoach, omnibus, passenger vehicle':'truck',
    'buses':                                                'truck',
    'bulldozer':                                            'truck',
    # 'rider'
    'minibike, motorbike':                                  'rider',
    'bicycle, bike, wheel, cycle':                          'rider',
    # 'person'
    'person, individual, someone, somebody, mortal, soul':  'person',
    # 'tunnel'
    'tunnel':                                               'tunnel',

}

def annotationConvert(annotationIn):
    annotationOut = Annotation()
    annotationOut.imgWidth = annotationIn.imgWidth
    annotationOut.imgHeight = annotationIn.imgHeight

    # for each label in the json file
    for obj in annotationIn.objects:
        label = obj.label

        if not label in labelTransferDict:
            print "Label '{}' not known.".format(label)
            continue

        newLabel = labelTransferDict[label]

        if newLabel != obj.label:
            print "    '{}' -> '{}'".format(obj.label, newLabel)

        obj.label = newLabel
        if obj.label != '':
            annotationOut.objects.append(obj)

    return annotationOut

def getAnnotation(img):
    ann = Annotation()
    ann.imgHeight, ann.imgWidth = img.shape[:2]

    R = img[:, :, 2]
    G = img[:, :, 1]
    B = img[:, :, 0]

    ObjectClassMasks = (R / 10) * 256 + G
    labelIds = np.unique(ObjectClassMasks)

    objId = 0
    polygons = []  # for test
    for labelId in labelIds:
        bImg = np.zeros(ObjectClassMasks.shape, dtype=np.uint8)
        indices = np.argwhere(ObjectClassMasks==labelId)
        bImg[indices[:,0], indices[:,1]]=255
        _,contours,hierarchy = cv2.findContours(bImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #RETR_TREE




        ADELabelName = ADE20KLabel[labelId]

        if not ADELabelName in labelTransferDict:
            ygoLabelName = 'unlabelled'
            print ('    ' + ADELabelName + '->' + ygoLabelName)
        else:
            ygoLabelName = labelTransferDict[ADELabelName]

        for contour in contours:
            obj = CsObject()
            obj.label = ygoLabelName
            obj.id = objId
            pntArr =  cv2.approxPolyDP(contour, 3, 1)
            # print pntArr
            for pl in pntArr:
                for p in pl:
                    obj.polygon.append(Point(np.int(p[0]), np.int(p[1])))
            ann.objects.append(obj)
            objId = objId + 1
    return ann


if __name__ == '__main__':
    if len(sys.argv) > 1:
        fileparam = sys.argv[1]

        if os.path.isdir(fileparam):
            for dirpath, dirnames, filenames in os.walk(fileparam):
                for filename in filenames:
                    # Skip non label files
                    if '_seg.png' not in filename:
                        continue

                    imagefile = os.path.join(dirpath, filename)
                    print("image file:" + imagefile)

                    img = cv2.imread(imagefile)
                    ann = getAnnotation(img)

                    jsonname = filename.replace('_seg.png', '.json')
                    jsonfile = os.path.join(dirpath, jsonname)
                    ann.toJsonFile(jsonfile)

        else:
            print('Oops!')
    else:
        print('Input a folder or an image!')
