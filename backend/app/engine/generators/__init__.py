from app.engine.generators import drag_order, drag_slot, encounter, fill_blank, listening, mcq

REGISTRY: dict = {"mcq":mcq.Generator,"fill_blank":fill_blank.Generator,"drag_slot":drag_slot.Generator,"drag_order":drag_order.Generator,"listening":listening.Generator,"encounter":encounter.Generator}
