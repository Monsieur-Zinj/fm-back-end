from fastapi import APIRouter, Depends, HTTPException
from .database import db
from models import Deck, Card
from .dependencies import get_current_user

router = APIRouter(prefix="/decks")

@router.post("")
async def create_deck(deck: Deck, current_user: dict = Depends(get_current_user)):
    deck.created_by = current_user["_id"]
    result = await db.decks.insert_one(deck.dict())
    return {"id": str(result.inserted_id)}

@router.get("")
async def get_decks(current_user: dict = Depends(get_current_user)):
    decks = await db.decks.find({
        "$or": [
            {"created_by": current_user["_id"]},
            {"is_public": True}
        ]
    }).to_list(None)
    return decks

@router.post("/{deck_id}/cards")
async def add_card(deck_id: str, card: Card, current_user: dict = Depends(get_current_user)):
    deck = await db.decks.find_one({"_id": deck_id})
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    if deck["created_by"] != current_user["_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    card.deck_id = deck_id
    result = await db.cards.insert_one(card.dict())
    return {"id": str(result.inserted_id)}

@router.get("/{deck_id}/cards")
async def get_deck_cards(deck_id: str):
    cards = await db.cards.find({"deck_id": deck_id}).to_list(None)
    return cards
