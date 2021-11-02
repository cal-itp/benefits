describe("Confirmation page spec", () => {
  beforeEach(() => {
    cy.visit("/")
    cy.get(".buttons .btn")
      .first()
      .click()
    cy.get(".buttons .btn")
      .click()
    cy.get(".buttons .btn")
      .click()
  })

  it("Confirms an eligible user", () => {
    cy.get("#sub").type("A1234567")
    cy.get("#name").type("Garcia")
    cy.get("input[type='submit']")
      .click()
    cy.contains("Great! You’re eligible for a discount!")
  })

  it("Confirms an ineligible user", () => {
    cy.get("#sub").type("A1234567")
    cy.get("#name").type("Bob")
    cy.get("input[type='submit']")
      .click()
    cy.contains("We can’t confirm your age")
    cy.contains("You may still be eligible for a discount, but we can’t verify your age with the DMV.")
  })

  it("Validates an invalid number/id field", () => {
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
