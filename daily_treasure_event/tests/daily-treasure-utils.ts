import { newMockEvent } from "matchstick-as"
import { ethereum, Address, BigInt } from "@graphprotocol/graph-ts"
import {
  ChestOpened,
  PremiumChestOpened,
  PremiumUserAdded,
  PremiumUserRemoved
} from "../generated/DailyTreasure/DailyTreasure"

export function createChestOpenedEvent(
  user: Address,
  timestamp: BigInt
): ChestOpened {
  let chestOpenedEvent = changetype<ChestOpened>(newMockEvent())

  chestOpenedEvent.parameters = new Array()

  chestOpenedEvent.parameters.push(
    new ethereum.EventParam("user", ethereum.Value.fromAddress(user))
  )
  chestOpenedEvent.parameters.push(
    new ethereum.EventParam(
      "timestamp",
      ethereum.Value.fromUnsignedBigInt(timestamp)
    )
  )

  return chestOpenedEvent
}

export function createPremiumChestOpenedEvent(
  user: Address,
  timestamp: BigInt
): PremiumChestOpened {
  let premiumChestOpenedEvent = changetype<PremiumChestOpened>(newMockEvent())

  premiumChestOpenedEvent.parameters = new Array()

  premiumChestOpenedEvent.parameters.push(
    new ethereum.EventParam("user", ethereum.Value.fromAddress(user))
  )
  premiumChestOpenedEvent.parameters.push(
    new ethereum.EventParam(
      "timestamp",
      ethereum.Value.fromUnsignedBigInt(timestamp)
    )
  )

  return premiumChestOpenedEvent
}

export function createPremiumUserAddedEvent(user: Address): PremiumUserAdded {
  let premiumUserAddedEvent = changetype<PremiumUserAdded>(newMockEvent())

  premiumUserAddedEvent.parameters = new Array()

  premiumUserAddedEvent.parameters.push(
    new ethereum.EventParam("user", ethereum.Value.fromAddress(user))
  )

  return premiumUserAddedEvent
}

export function createPremiumUserRemovedEvent(
  user: Address
): PremiumUserRemoved {
  let premiumUserRemovedEvent = changetype<PremiumUserRemoved>(newMockEvent())

  premiumUserRemovedEvent.parameters = new Array()

  premiumUserRemovedEvent.parameters.push(
    new ethereum.EventParam("user", ethereum.Value.fromAddress(user))
  )

  return premiumUserRemovedEvent
}
