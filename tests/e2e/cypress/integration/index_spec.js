describe("Index page spec", () => {
    it("Asks user to choose a transit provider", () => {
        cy.visit("/")

        cy.contains("Choose your transit provider")
    })
})
