import { ChestOpened, User } from "../generated/schema";
import { ChestOpened as ChestOpenedEvent, PremiumChestOpened as PremiumChestOpenedEvent } from "../generated/DailyTreasureEvent/DailyTreasureEvent";
import { BigInt } from "@graphprotocol/graph-ts";

export function handleChestOpened(event: ChestOpenedEvent): void {
  let user = User.load(event.params.user.toHex());
  if (user == null) {
    user = new User(event.params.user.toHex());
    user.lifetimeChestCount = 0;
    user.lifetimePremiumChestCount = 0;
    user.lifetimeTotalChestCount = 0;
  }

  user.lifetimeChestCount = user.lifetimeChestCount + 1;
  user.lifetimeTotalChestCount = user.lifetimeTotalChestCount + 1;
  user.save();

  let chestOpened = new ChestOpened(event.transaction.hash.toHex());
  chestOpened.user = user.id;
  chestOpened.timestamp = event.block.timestamp;
  chestOpened.isPremium = false;
  chestOpened.save();
}

export function handlePremiumChestOpened(event: PremiumChestOpenedEvent): void {
  let user = User.load(event.params.user.toHex());
  if (user == null) {
    user = new User(event.params.user.toHex());
    user.lifetimeChestCount = 0;
    user.lifetimePremiumChestCount = 0;
    user.lifetimeTotalChestCount = 0;
  }

  user.lifetimePremiumChestCount = user.lifetimePremiumChestCount + 1;
  user.lifetimeTotalChestCount = user.lifetimeTotalChestCount + 1;
  user.save();

  let chestOpened = new ChestOpened(event.transaction.hash.toHex());
  chestOpened.user = user.id;
  chestOpened.timestamp = event.block.timestamp;
  chestOpened.isPremium = true;
  chestOpened.save();
}
