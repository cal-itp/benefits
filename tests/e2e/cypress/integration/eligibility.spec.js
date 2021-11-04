describe("Confirms a user's eligibility status", () => {
  beforeEach(() => {
    cy.visit("/")
    cy.get(".buttons .btn")
      .first()
      .click()
    cy.get(".buttons .btn")
      .click()
  })

  it("Takes user to eligibility confirmation page", () => {
    cy.contains("Ready to continue")
      .then(($e) => {
        expect($e).attr("href").to.have.string("eligibility/confirm")
      })

    cy.get(".buttons .btn")
      .click()

    cy.contains("Let’s see if we can confirm your age")
    cy.contains("CA driver’s license or ID number *")
  })

  it("From the confirmation page, confirms an eligible user", () => {
    cy.get(".buttons .btn")
      .click()
    cy.get("#sub").type("A1234567")
    cy.get("#name").type("Garcia")
    cy.get("input[type='submit']")
      .click()
    cy.contains("Great! You’re eligible for a discount!")
  })

  it("From the confirmation page, confirms an ineligible user", () => {
    cy.get(".buttons .btn")
      .click()

    cy.get("#sub").type("A1234567")
    cy.get("#name").type("Bob")
    cy.get("input[type='submit']")
      .click()
    cy.contains("We can’t confirm your age")
    cy.contains("You may still be eligible for a discount, but we can’t verify your age")
  })

  it("From the confirmation page, validates an invalid number/id field", () => {
    cy.get(".buttons .btn")
      .click()

    cy.get("#sub").type("A12347")
    cy.get("#name").type("Garcia")
    cy.get("input[type='submit']")
      .click()
    cy.contains("Check your input. The format looks wrong.")
    cy.get("#id_sub")
      .then(($e) => {
        expect($e).to.have.css("border-color", "rgb(222, 12, 12)")
      })
  })
})
