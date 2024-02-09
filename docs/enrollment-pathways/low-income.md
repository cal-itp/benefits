# Low-income

## Overview

This use case describes a feature in the Cal-ITP Benefits app that allows Californians to verify their active participation in the CalFresh Program—as a proxy for low-income status—to receive reduced fares for transit when paying by contactless debit or credit card at participating transit operators in California.

**Actor:** A person who uses public transit in California. For benefit eligibility, a “low-income rider” is a person who has received [CalFresh benefits](https://www.cdss.ca.gov/food-nutrition/calfresh) in any of the previous three months.

**Goal:** To verify a transit rider’s financial need so they receive reduced fares when paying by contactless debit or credit card.

**Precondition:** The California transit operator offers fixed route service, has installed and tested validator hardware necessary to collect fares using contactless payment on bus or rail lines, and the operator has a policy in place to offer a transit discount to low-income riders.

## Basic Flow

1. The transit rider visits the web application at `benefits.calitp.org` in a browser on their desktop computer.

2. The transit rider chooses the transit operator that serves their area.

3. The transit rider chooses to verify their eligibility as a participant in the [CalFresh Program](https://www.cdss.ca.gov/food-nutrition/calfresh).

4. The transit rider authenticates with their existing [Login.gov](Login.gov) account or, if they don’t have one, creates a [Login.gov](Login.gov) account.

5. The Cal-ITP Benefits app interfaces with the [California Department of Transportation](https://dot.ca.gov/) Identity Gateway (IdG) to verify benefit eligibility. The IdG uses personal information shared by [Login.gov](Login.gov) to verify CalFresh participation status.

6. The IdG uses the response provided by the California Department of Social Services (CDSS) to determine the rider’s eligibility for a transit benefit.

7. The IdG then passes the response from CDSS as low-income status = TRUE to the Cal-ITP Benefits app to indicate the person is eligible for a benefit.

8. The transit rider provides the debit or credit card details they use to pay for transit to Littlepay, the payment processor that facilitates transit fare collection.

9. The app registers the low-income benefit with the transit rider’s debit or credit card.

## Alternative Flows

- Suppose the transit rider does not have a desktop computer. In this case, they open the web application at `benefits.calitp.org` in a mobile browser on their iOS or Android tablet or mobile device to complete enrollment using the basic flow.

- Suppose the transit rider cannot authenticate with [Login.gov](Login.gov), or will not create an account. In either case, the app cannot determine their CalFresh Program participation status and they cannot enroll their contactless debit or credit card for a reduced fare.

- Suppose the IdG returns a status of `FALSE` for CalFresh Program participation status. In that case, the Cal-ITP Benefits app will not allow the transit rider to enroll their contactless debit or credit card for a reduced fare.

- Suppose the debit or credit card expires or is canceled by the issuer. In that case, the transit rider must repeat the basic flow to register a new debit or credit card.

- When the initial transit benefit enrollment period ends after one year from the date of enrollment, the transit rider must repeat the basic flow to re-enroll.

- Suppose the transit rider attempts to re-enroll for a transit benefit as a CalFresh Program participant three months after their enrollment period started. The app will inform them they must wait re-enroll within 14 days of the benefit expiration.

- Suppose the transit rider doesn’t re-enroll for a transit benefit after one year, but continues paying for transit using the card they registered. The transit operator will charge the rider full fare.

- If the transit rider uses more than one debit or credit card to pay for transit, they repeat the basic flow for each card.

## Postcondition

The transit rider receives a fare reduction each time they use the debit or credit card they registered to pay for transit rides. The number of times they can use the card to pay for transit is unlimited, but the benefit expires one year after enrollment.

## Benefits

- The transit rider no longer needs cash to pay for transit rides.

- The transit rider doesn’t have to lock up funds on a closed-loop card offered by the transit agency.

- The transit rider pays for transit rides with their debit or credit card, just as they do for groceries, a cup of coffee, or any other good or service.

- The transit rider can enroll in a transit benefit from home when convenient; they do not have to visit a transit agency in person.

- The transit rider does not have to prove income eligibility with the transit agency. The app simply uses their participation in the CalFresh program to confirm eligibility for a transit benefit.

- The transit agency doesn't have to craft and policy for a low-icome discount; they simply use the approach implemented in the Cal-ITP Benefits application. As more agencies adopt the application, they also adopt a standard policy for transit benefits. 

- Secure state and federal solutions manage the transit rider’s personal identifiable information (PII): [Login.gov](Login.gov) and the California Department of Technology Identity Gateway (IdG). Transit riders do not have to share personal information with local transit operators.

- Benefit enrollment takes minutes rather than days or weeks.

- Benefit enrollment doesn’t require online accounts with private companies.

## Example Scenario

A CalFresh Program participant uses public transit regularly. They don’t have a car and depend on buses to get to appointments and do errands that take too long to use their bicycle. Even though this person already qualifies for benefits from the California Department of Social Services, they had to navigate another extensive, in-person eligibility process with different requirements to qualify for reduced fares from their local transit agency. They now receive a 50% fare reduction but have to pay for transit rides using the closed loop card provided by the operator to receive the reduced fare. It’s frustrating and inconvenient to reload this closed loop card in $10 payments every week, especially because they sometimes they could use the money tied up on the card to make ends meet. In summary, this person pays for daily expenses using three forms of payment: their Electronic Benefits Transfer (EBT) card for eligible items, their agency card for transportation, and their bank card (or cash) for everything else.

The transit operator serving their region of California implements contactless payments on fixed bus routes throughout the service area. This rider uses `benefits.calitp.org` on their mobile device to confirm their participation in the CalFresh Program offered by CDSS and registers their debit card for reduced fares. They tap to pay when boarding buses in their area and are automatically charged the reduced fare. While they still need to manage funds on their EBT card *and* their bank card, they no longer need to use their transit operator card to pay for transit. Best of all, they have complete access to all funds in their weekly budget. If other expenses are higher one week, they can allocate additional funds to those areas and ride transit less.
