from robusta.api import *

@action
def delete_unclaimed_volume(event: EventEvent):
    logging.error(f"job restart was called on event without job")