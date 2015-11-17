from anthrocon_plugin import *

anthrocon_config = parse_config(__file__)
c.include_plugin_config(anthrocon_config)

c.TABLE_OPTS = [
    (0.5, 'Half Table'),
    (1.0, 'Single Table'),
    (1.5, 'Single+Half Table'),
    (2.0, 'Double Table'),
    (3.0, 'Triple Table'),
    (4.0, 'Quad Table'),
    (4.5, 'Island Table')
]

c.ADMIN_TABLE_OPTS = [(0.0, 'No Table')] + c.TABLE_OPTS

c.TABLE_PRICES = {0: 0, 0.5: 45, 1: 110, 1.5: 210, 2: 350, 3: 600, 4: 900, 4.5: 1200}

c.PREREG_TABLE_OPTS = [(count, '{}: ${}'.format(desc, c.TABLE_PRICES[count])) for count, desc in c.TABLE_OPTS]

c.DEALER_BADGE_PRICE = c.BADGE_PRICE

c.TABLE_EXTRA_OPTS = [(amt, '+ ${}: {}'.format(amt, desc) if amt else desc) for amt, desc in c.TABLE_EXTRA_OPTS]