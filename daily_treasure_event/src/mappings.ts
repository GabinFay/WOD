import { ChestOpened, User } from "../generated/schema";
import { ChestOpened as ChestOpenedEvent, PremiumChestOpened as PremiumChestOpenedEvent, PremiumUserAdded, PremiumUserRemoved } from "../generated/DailyTreasureEvent/DailyTreasureEvent";
import { BigInt } from "@graphprotocol/graph-ts";

function getOrCreateUser(address: string): User {
  let user = User.load(address);
  if (user == null) {
    user = new User(address);
    user.lifetimeChestCount = 0;
    user.lifetimePremiumChestCount = 0;
    user.lifetimeTotalChestCount = 0;
    user.isPremiumUser = false;
  }
  return user;
}

export function handleChestOpened(event: ChestOpenedEvent): void {
  let user = getOrCreateUser(event.params.user.toHex());

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
  let user = getOrCreateUser(event.params.user.toHex());

  user.lifetimePremiumChestCount = user.lifetimePremiumChestCount + 1;
  user.lifetimeTotalChestCount = user.lifetimeTotalChestCount + 1;
  user.save();

  let chestOpened = new ChestOpened(event.transaction.hash.toHex());
  chestOpened.user = user.id;
  chestOpened.timestamp = event.block.timestamp;
  chestOpened.isPremium = true;
  chestOpened.save();
}

export function handlePremiumUserAdded(event: PremiumUserAdded): void {
  let user = getOrCreateUser(event.params.user.toHex());
  user.isPremiumUser = true;
  user.save();
}

export function handlePremiumUserRemoved(event: PremiumUserRemoved): void {
  let user = getOrCreateUser(event.params.user.toHex());
  user.isPremiumUser = false;
  user.save();
}
