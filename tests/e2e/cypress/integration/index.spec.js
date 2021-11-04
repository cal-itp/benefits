describe("Index page spec", () => {
  beforeEach(() => {
    cy.visit("/")
  })

  it("Gives user transit provider options", () => {
    cy.contains("Choose your transit provider")
      .siblings(".btn")
      .should('not.be.empty')
      .each(($e) => {
        expect($e).attr("href").to.match(/\/[a-z]{3,}$/)
      })
  })

  it("Takes user to a transit provider page", () => {
    cy.get(".buttons .btn")
      .first()
      .click()

    cy.contains("Let’s do it!")
      .then(($e) => {
        expect($e).attr("href").to.match(/\/eligibility\/$/)
      })
  })

  it("Has a payment options page link", () => {
    cy.contains("Payment Options")
  })

  it("Has a help page link", () => {
    cy.contains("Help")
  })

})
