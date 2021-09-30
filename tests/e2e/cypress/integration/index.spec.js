describe("Index page spec", () => {
    it("Gives user transit provider options", () => {
        cy.visit("/")

        cy.contains("Choose your transit provider")
          .siblings(".btn")
          .should('not.be.empty')
          .each(($e) => {
              expect($e).attr("href").to.match(/\/[a-z]{3,}$/)
          })
    })
})
