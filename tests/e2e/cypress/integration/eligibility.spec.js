describe("Eligibility page spec", () => {
  it("Takes user to eligibility confirmation page", () => {
    cy.visit("/")

    cy.get(".buttons .btn")
      .first()
      .click()

    cy.get(".buttons .btn")
      .click()

    cy.contains("Ready to continue")
      .then(($e) => {
        expect($e).attr("href").to.have.string("eligibility/confirm")
      })

    cy.get(".buttons .btn")
      .click()

    cy.contains("Let’s see if we can confirm your age with the DMV")
    cy.contains("CA driver’s license or ID number *")
  })
})
