The use cases documented on this page focus on how the system is supposed to work from the perspective of the end user.

### Use case: Enroll contactless card to receive transit benefit

**Primary Actor**: Transit rider

**Systems**: Benefits app, payment processor

**Preconditions**:

- Transit rider has confirmed their eligibility with the Benefits app
- Transit rider has their contactless card information available
- Benefits app is able to contact the payment processor

**Trigger**: Transit rider initiates the enrollment phase

**Basic flow**:

1. Transit rider enters their contactless card information
2. Benefits app passes that information to the payment processor to enroll the card
3. Payment processor successfully enrolls card

**Alternate flows**:

- 3a. Payment processor returns with one of the following errors: card verification failed, token is invalid, or general server error
    - 3a1. Transit rider chooses to retry, starting back at initiating the enrollment phase
    - 3b1. Transit rider leaves the Benefits app

**Postconditions**:

- Transit rider's contactless card is enrolled to receive the transit benefit
