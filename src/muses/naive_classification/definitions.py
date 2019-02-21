from keras import layers
from keras import models
from keras import optimizers
from keras.applications import VGG19, Xception
from django.conf import settings
import os

loss = 'categorical_crossentropy'
optimizer = optimizers.RMSprop(lr=1e-4, decay=1e-6)
metrics = ['acc']
DATASET_DIR = settings.PROJECT_DIR(os.path.join('..', '..', 'datasets'))


# Pre-trained Xception model with the last 4 layers unfrozen and custom top
def create_xception_model(target_size, num_classes):
    xception_conv = Xception(weights='imagenet', include_top=False, input_shape=(target_size[0], target_size[1], 3))
    for layer in xception_conv.layers[:-4]:
        layer.trainable = False

    # Create the model
    model = models.Sequential()

    # Add the inception convolutional base model
    model.add(xception_conv)

    # Add new layers
    model.add(layers.Flatten())
    model.add(layers.Dense(2048, activation='relu'))
    model.add(layers.Dropout(0.5))
    model.add(layers.Dense(num_classes, activation='softmax'))
    model.compile(
        loss=loss,
        optimizer=optimizer,
        metrics=metrics
    )
    return model


# Pre-trained VGG19 model with the last 4 layers unfrozen and custom top
def create_vgg_model(target_size, num_classes):
    vgg_conv = VGG19(weights='imagenet', include_top=False, input_shape=(target_size[0], target_size[1], 3))
    for layer in vgg_conv.layers[:-4]:
        layer.trainable = False
    vgg_conv.trainable = False

    # Create the model
    model = models.Sequential()

    # Add the vgg convolutional base model
    model.add(vgg_conv)

    # Add new layers

    model.add(layers.Flatten())
    model.add(layers.Dense(256, activation='relu'))
    model.add(layers.Dropout(0.4))
    model.add(layers.Dense(num_classes, activation='softmax'))


    # model.add(layers.Flatten())
    # model.add(layers.Dense(1024, activation='relu'))
    # model.add(layers.Dropout(0.5))
    # model.add(layers.Dense(num_classes, activation='softmax'))
    model.compile(
        loss=loss,
        optimizer=optimizer,
        metrics=metrics
    )
    return model


# Custom model
def create_naive_model(target_size, num_classes):
    input_shape = target_size + (3,)
    model = models.Sequential()
    model.add(layers.Conv2D(
        32,
        (3, 3),
        padding='same',
        activation='relu',
        input_shape=input_shape
    ))
    # model.add(layers.MaxPooling2D((2, 2)))
    # model.add(layers.Dropout(0.25))
    model.add(layers.Conv2D(
        32,
        (3, 3),
        padding='same',
        activation='relu'
    ))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Dropout(0.25))
    model.add(layers.Conv2D(
        64,
        (3, 3),
        padding='same',
        activation='relu'
    ))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Dropout(0.25))
    model.add(layers.Conv2D(
        64,
        (3, 3),
        padding='same',
        activation='relu'
    ))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Dropout(0.25))
    model.add(layers.Conv2D(
        128,
        (3, 3),
        padding='same',
        activation='relu'
    ))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Dropout(0.25))
    model.add(layers.Conv2D(
        128,
        (3, 3),
        padding='same',
        activation='relu'
    ))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Dropout(0.25))
    model.add(layers.Flatten())
    model.add(layers.Dense(512, activation='relu'))
    model.add(layers.Dropout(0.5))
    model.add(layers.Dense(num_classes, activation='softmax'))
    model.compile(
        loss=loss,
        optimizer=optimizer,
        metrics=metrics
    )
    return model

# Class keys should start at 0 and end at the number of classes-1
# Commented classes might be added if there is more data available
classes = {
    '0': 'scarab',
    '1': 'shabti',
    '2': 'stela',
    '3': 'ostracon',
    '4': 'ring',
    '5': 'mummy',
    '6': 'bead',
    '7': 'coffin',
    '8': 'papyrus',
    '9': 'statue',
    # '9': 'standing statue',
    '10': 'coin',
    '11': 'vessel',
    '12': 'relief',
    '13': 'plaque',
    # '14': 'amulet',
    '14': 'shard',
    '15': 'earring',
    '16': 'bowl',
    '17': 'jar',
    '18': 'pendant',
    '19': 'canopic jar',
    # '22': 'horuscippus',
    # '23': 'heart scarab',
    # '24': 'linen',
    # '25': 'mirror',
    # '26': 'basket',
    # '27': 'axe',
    # '28': 'arrow',
    # '29': 'talatat',
    '20': 'sealing',
    # '31': 'palette',
    # '32': 'offering table',
    '21': 'vase',
    # '34': 'dish',
    '22': 'cone',
    # '36': 'bracelet',
    # '23': 'necklace',
}

# A list of synonyms and search fields
# The search fields are used to retrieve similar objects
synonyms_extended = {
    'scarab': {
        'synonyms': ['scarab', 'scarabee', 'scarabs'],
        'exclude': [],
        'fields': ['title_en', ('object_type_en', 2), ('primary_object_type_en', 4),],
    },
    'shabti': {
        'synonyms': ['ushabti', 'shabti', 'shabty', 'oesjebti', 'ushabtis', 'shabtis', 'shabtys'],
        'exclude': [],
        'fields': ['title_en', ('object_type_en', 2), ('primary_object_type_en', 3),],
    },
    'stela': {
        'synonyms': ['stela', 'stele', 'steles', 'stelae', 'stelas', 'stelaes'],
        'exclude': [],
        'fields': ['title_en', ('object_type_en', 2), ('primary_object_type_en', 3),],
    },
    'ostracon': {
        'synonyms': ['ostracon', 'ostracons', 'ostraca'],
        'exclude': [],
        'fields': ['title_en', ('object_type_en', 2), ('primary_object_type_en', 3),],
    },
    'ring': {
        'synonyms': ['ring', 'rings'],
        'exclude': [],
        'fields': ['title_en', ('object_type_en', 2), ('primary_object_type_en', 3),],
    },
    'mummy': {
        'synonyms': ['mummy', 'mummie', 'human remains', 'mummified'],
        'exclude': ['coffin', 'inner coffin', 'outer coffin', 'mummy board', 'coffins'],
        'fields': ['title_en', ('object_type_en', 2), ('primary_object_type_en', 3),],
    },
    'bead': {
        'synonyms': ['bead', 'beads', 'string of beads', 'necklace', 'necklaces',],
        'exclude': ['bracelet', 'bracelets', 'pendant', 'scarab', 'statue'],
        'fields': ['title_en', ('object_type_en', 2), ('primary_object_type_en', 3),],
    },
    # 'necklace': {
    #     'synonyms': ['string of beads', 'necklace', 'necklaces', 'chain', 'chains', 'collar'],
    #     'exclude': ['pendant', 'statue', 'bracelets', 'statuette'],
    #     'fields': ['title_en', ('object_type_en', 2), ('primary_object_type_en', 4),],
    # },
    'coffin': {
        'synonyms': ['coffin', 'inner coffin', 'outer coffin', 'mummy board', 'coffins'],
        'exclude': [],
        'fields': ['title_en', ('object_type_en', 2), ('primary_object_type_en', 3),],
    },
    'papyrus': {
        'synonyms': ['papyrus', 'book of the dead', 'amduat', 'amdoeat', 'amduats', 'amdoeats'],
        'exclude': ['shard', 'fragment', 'shards', 'fragments', 'mirror', 'mirrors'],
        'fields': ['title_en', ('object_type_en', 2), ('primary_object_type_en', 3),],
    },
    'statue': {
        'synonyms': ['statue', 'statuette', 'kneeling statue', 'standing statue', 'statues', 'statuettes'],
        'exclude': ['shard', 'fragment', 'shards', 'fragments'],
        'fields': ['title_en', ('object_type_en', 2), ('primary_object_type_en', 3),],
    },
    'coin': {
        'synonyms': ['coin', 'tetradrachme', 'tetradrachm', 'coins', 'tetradrachmes', 'tetradrachms'],
        'exclude': [],
        'fields': ['title_en', ('object_type_en', 2), ('primary_object_type_en', 3),],
    },
    'vessel': {
        'synonyms': ['vessel', 'vat', 'container', 'vessels', 'vats', 'containers'],
        'exclude': ['shard', 'fragment', 'shards', 'fragments'],
        'fields': ['title_en', ('object_type_en', 2), ('primary_object_type_en', 3),],
    },
    'relief': {
        'synonyms': ['relief', 'reliefs'],
        'exclude': [],
        'fields': ['title_en', ('object_type_en', 2), ('primary_object_type_en', 3),],
    },
    'plaque': {
        'synonyms': ['plaque', 'plaques'],
        'exclude': [],
        'fields': ['title_en', ('object_type_en', 2), ('primary_object_type_en', 3),],
    },
    # 'amulet': {
    #     'synonyms': ['amulet', 'amulet-pendant', 'amulet-pendants', 'amulets'],
    #     'exclude': [],
    #     'fields': ['title_en', ('object_type_en', 2), ('primary_object_type_en', 4),],
    # },
    'shard': {
        'synonyms': ['shard', 'shards', 'fragments'], #fragment
        'exclude': [],
        'fields': ['title_en', ('object_type_en', 2), ('primary_object_type_en', 3),],
    },
    'earring': {
        'synonyms': ['earring', 'earrings', 'ear'], #, 'ear ring', 'ear rings'
        'exclude': [],
        'fields': ['title_en', ('object_type_en', 2), ('primary_object_type_en', 3),],
    },
    'bowl': {
        'synonyms': ['bowl', 'kom', 'bowls'],
        'exclude': ['shard', 'fragment', 'shards', 'fragments'],
        'fields': ['title_en', ('object_type_en', 2), ('primary_object_type_en', 3),],
    },
    'jar': {
        'synonyms': ['jar', 'pot', 'jars', 'pots'],
        'exclude': ['canopic jar', 'canope', 'canopes', 'canopic jars', 'shard', 'fragment', 'shards', 'fragments'],
        'fields': ['title_en', ('object_type_en', 2), ('primary_object_type_en', 3),],
    },
    # 'bottle': {
    #     'synonyms': ['bottle', 'bottles'],
    #     'exclude': ['shard', 'fragment', 'shards', 'fragments'],
    #     'fields': ['title_en', ('object_type_en', 2), ('primary_object_type_en', 4),],
    # },
    'pendant': {
        'synonyms': ['pendant', 'pendants', 'hanger', 'amulet-pendant', 'amulet-pendants'],
        'exclude': [],
        'fields': ['title_en', ('object_type_en', 2), ('primary_object_type_en', 3),],
    },
    'canopic jar': {
        'synonyms': ['canopic jar', 'canope', 'canopes', 'canopic jars'],
        'exclude': ['shard', 'fragment', 'shards', 'fragments', 'canopic box', 'canopic chest'],
        'fields': ['title_en', ('object_type_en', 2), ('primary_object_type_en', 3),],
    },
    # 'horuscippus': {
    #     'synonyms': ['horuscippus', 'cippus of horus', 'cippus with horus', 'stele; horus; bes', 'stela; horus; bes',
    #                 'cippus/ horus stela', 'horus-stele', 'cippus-horus stela', 'horus stele'],
    #     'exclude': [],
    #     'fields': ['title_en', ('object_type_en', 2), ('primary_object_type_en', 4),],
    # },
    # 'heart scarab': ['heart scarab'],
    # 'linen': ['linen', 'linnen', 'cloth', 'mummy coat', 'cloths'],
    # 'mirror': ['mirror', 'mirrors'],
    # 'basket': ['basket', 'baskets'],
    # 'axe': ['axe', 'ax', 'axes'],
    # 'arrow': ['arrow', 'arrows'],
    # 'talatat': ['talatat'],
    'sealing': {
        'synonyms': ['sealing', 'seal impression', 'seal'],
        'exclude': [],
        'fields': ['title_en', ('object_type_en', 2), ('primary_object_type_en', 3),],
    },
    # 'palette': ['palette', 'palet', 'palets', 'palettes'],
    # 'offering table': ['offering table', 'offer table'],
    'vase': {
        'synonyms': ['vase', 'vaas', 'vases'],
        'exclude': ['shard', 'fragment', 'shards', 'fragments'],
        'fields': ['title_en', ('object_type_en', 2), ('primary_object_type_en', 3),],
    },
    # 'dish': ['dish', 'schaal', 'dishes'],
    'cone': {
        'synonyms': ['cone', 'cones', 'funerary cone', 'funerary cones'],
        'exclude': [],
        'fields': ['title_en', ('object_type_en', 2), ('primary_object_type_en', 3),],
    },
    # 'bracelet': ['bracelet', 'bracelets'],
}


# Get a list of synonyms
synonyms = {key: value['synonyms'] for key, value in synonyms_extended.items()}
exclude = {key: value['exclude'] for key, value in synonyms_extended.items()}

# These could be used in the future to automatically detect the material of an object
materials = {
    '0': 'faience',
    '1': 'bronze',
    '2': 'papyrus',
    '3': 'wool',
    '4': 'wood',
    '5': 'copper',
    '6': 'gold',
    '7': 'silver',
    '8': 'carnelian',
    '9': 'glass',
    '10': 'clay',
    '11': 'stone',
    '12': 'granite',
    '13': 'pottery',
    '14': 'limestone',
    '15': 'marble',
    '16': 'sandstone',
    '17': 'terracotta',
    '18': 'steatite',
    # '0': 'anhydrite',
    # '10': 'reed',
    # '100': 'bone',
    # '101': 'claw',
    # '102': 'eggshell',
    # '103': 'fat',
    # '104': 'feather',
    # '105': 'glue',
    # '106': 'gut',
    # '107': 'hair',
    # '108': 'horn',
    # '109': 'ivory',
    # '11': 'brass',
    # '110': 'leather',
    # '111': 'mother',
    # '112': 'parchment',
    # '113': 'pearl',
    # '114': 'shell',
    # '115': 'tortoise',
    # '116': 'unspecified',
    # '117': 'ashes',
    # '118': 'charcoal',
    # '119': 'cotton',
    # '120': 'date-palm',
    # '2': 'flax',
    # '122': 'halfa',
    # '123': 'hemp',
    # '125': 'rush',
    # '126': 'silk',
    # '127': 'unspecified',
    # '129': 'bitumen',
    # '13': 'electrum',
    # '130': 'coal',
    # '131': 'frankincense',
    # '132': 'gum',
    # '133': 'myrrh',
    # '134': 'oil',
    # '135': 'resin',
    # '136': 'straw',
    # '138': 'christ',
    # '139': 'acacia',
    # '14': 'unspecified',
    # '140': 'almond',
    # '141': 'ash',
    # '142': 'beech',
    # '143': 'birch',
    # '144': 'box',
    # '145': 'carob',
    # '146': 'cedar',
    # '147': 'cypress',
    # '148': 'date',
    # '149': 'dom',
    # '15': 'antimony',
    # '150': 'ebony',
    # '151': 'elm',
    # '152': 'fir',
    # '153': 'hornbeam',
    # '154': 'juniper',
    # '155': 'lime',
    # '156': 'liquidambar',
    # '157': 'oak',
    # '158': 'persea',
    # '159': 'pine',
    # '160': 'sycamore',
    # '161': 'tamarisk',
    # '162': 'unspecified',
    # '163': 'willow',
    # '164': 'yew',
    # '18': 'iron',
    # '19': 'lead',
    # '2': 'gesso',
    # '20': 'platinum',
    # '22': 'tin',
    # '23': 'unspecified',
    # '24': 'agate',
    # '25': 'amazonite',
    # '26': 'amethyst',
    # '27': 'anhydrite',
    # '28': 'beryl',
    # '30': 'chalcedony',
    # '31': 'chrysoprase',
    # '32': 'emery',
    # '33': 'felspar',
    # '34': 'fluorite',
    # '35': 'galena',
    # '36': 'garnet',
    # '37': 'graphite',
    # '38': 'gypsum',
    # '39': 'jade',
    # '4': 'glaze',
    # '40': 'jadeite',
    # '41': 'lapis',
    # '42': 'malachite',
    # '43': 'mica',
    # '44': 'microcline',
    # '45': 'green',
    # '46': 'amazon-stone',
    # '47': 'nephrite',
    # '48': 'olivinemi',
    # '49': 'onyx',
    # '5': 'incense',
    # '50': 'orpiment',
    # '51': 'peridot',
    # '52': 'quartz',
    # '53': 'rock',
    # '54': 'red',
    # '55': 'salt',
    # '56': 'sardonyx',
    # '57': 'sulphur',
    # '58': 'turquoise',
    # '59': 'unspecified',
    # '6': 'mortar',
    # '60': 'yellow',
    # '61': 'nile',
    # '62': 'alum',
    # '63': 'chrysocolla',
    # '65': 'sand',
    # '66': 'unspecified',
    # '68': 'iceland',
    # '69': 'anorthosite',
    # '7': 'plaster',
    # '70': 'basalt',
    # '71': 'breccia',
    # '72': 'calcite',
    # '73': 'diorite',
    # '74': 'dolerite',
    # '75': 'dolomite',
    # '76': 'flint/chert',
    # '77': 'gabbro',
    # '79': 'granodiorite',
    # '80': 'greywacke',
    # '81': 'jasper',
    # '84': 'mudstone',
    # '85': 'obsidian',
    # '86': 'porphyry',
    # '87': 'quartzite',
    # '89': 'serpentinite',
    # '90': 'silicified',
    # '91': 'siltstone',
    # '92': 'slate',
    # '94': 'soap',
    # '95': 'syenite',
    # '96': 'unspecified',
    # '97': 'volcanic',
    # '98': 'tuff',
    # '99': 'beeswax'
}
