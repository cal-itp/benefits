describe("Index page - Internationalization spec", () => {
  beforeEach(() => {
    cy.visit("/")
  })

  it("Gives user Spanish language option", () => {
    cy.get("#header").should("contain", "Español")
    cy.get("#header").should("not.contain", "English")
  })

  it("Changes the language to Spanish", () => {
    cy.contains("Español")
      .click()

    cy.contains("La nueva forma de pagar")
    cy.get("#header").should("not.contain", "Español")
    cy.get("#header").should("contain", "English")
  })

  it("Changes the language from Spanish back to English", () => {

    cy.contains("Español")
      .click()

    cy.contains("La nueva forma de pagar")
    cy.get("#header").should("not.contain", "Español")
    cy.get("#header").should("contain", "English")
    cy.contains("English")
      .click()

    cy.get("#main-content").should("contain", "The new way to pay for transit")
    cy.get("#main-content").should("not.contain", "La nueva forma de pagar")
  })

  it("Changes the language to Spanish from any page", () => {
    cy.get(".buttons .btn")
      .first()
      .click()

    cy.contains("Español")
      .click()

    cy.get("#main-content").should("contain", "¡Hagámoslo!")
    cy.get("#main-content").should("not.contain", "Let’s do it!")
  })
})
