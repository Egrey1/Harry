# Deprecated: this module was removed in favour of direct use of Country/Market/Item objects.
# If you still see imports from here, update the callers to use the object API:
#   - country.inventory / item.quantity
#   - country.market.inventory / Item.price
#   - use DB-level helpers in `classes.game_objects` if you need centralized mutation

raise RuntimeError('market/library/functions.py has been removed; update call sites to use Country/Market/Item objects')