# Manual tests

This page lists manual testing scripts for various flows.

## Getting started

In order to test a complete enrollment flow in the app, you will need to use appropriate test credentials for the flow and associated identity provider(s) (IdPs).

- See the tutorial on [Using the Login.gov sandbox](../tutorials/logingov-sandbox.md)
- The [Benefits Test Data document](https://docs.google.com/document/d/1bFynuiLy9POXYEYnLVEQJpAm1TVqlappN9lU9ev3Bvg/edit?tab=t.0) has more information for Login.gov and other IdPs / flows.

### Agency cards

To test the agency card enrollment pathway, use the following test credentials:

- [Courtesy Cards (MST)](https://docs.google.com/document/d/1bFynuiLy9POXYEYnLVEQJpAm1TVqlappN9lU9ev3Bvg/edit#heading=h.l2jcqsl4s6rh)
- [Reduced Fare Mobility ID (SBMTD)](https://docs.google.com/document/d/1bFynuiLy9POXYEYnLVEQJpAm1TVqlappN9lU9ev3Bvg/edit#heading=h.rkuhoc19aku7)

### Payment cards

To test the Littlepay or Switchio card enrollment flows, use test [Payment card information](https://docs.google.com/document/d/1bFynuiLy9POXYEYnLVEQJpAm1TVqlappN9lU9ev3Bvg/edit#heading=h.6l8f6lihq1vz), along with any fake name, any CVV and an expiration date in the future.

## Keyboard testing

Keyboard testing refers to test the app on a desktop/laptop machine _without_ using a mouse/trackpad. To do so, use <kbd>Tab</kbd> to focus on a button or link, and <kbd>Enter</kbd> to select a button or link.

Make sure:

- All links and buttons have a visible indication that the targeted item is focused.
- All modals close by pressing <kbd>Escape</kbd>.
- The skip nav, a link with the text `Skip to main content` / `Saltar al contenido principal` should appear on the first tab press.

## Spanish translation testing

1. Open the [test environment Benefits application](https://test-benefits.calitp.org/) in the test environment using a supported browser.
1. Click the **Español** button on the right side of the application header, to switch the application language to Spanish.
1. Click **Elija su Proveedor** and choose **Monterey-Salinas Transit** as your transit agency.
1. Follow the **Adulto mayor / Older adult** enrollment pathway to completion using [test data](https://docs.google.com/document/d/1bFynuiLy9POXYEYnLVEQJpAm1TVqlappN9lU9ev3Bvg/edit?usp=sharing). You will need a cell phone, a test Login.gov account and test Littlepay card credentials.
1. Follow the **Veterano de EE. UU. / Veterans** enrollment pathway to completion using [test data](https://docs.google.com/document/d/1bFynuiLy9POXYEYnLVEQJpAm1TVqlappN9lU9ev3Bvg/edit?usp=sharing). You will need a cell phone, a test Login.gov account and test Littlepay card credentials.
1. Follow the **Tarjeta de cortesía de MST / Courtesy Card** pathway to completion using [test data](https://docs.google.com/document/d/1bFynuiLy9POXYEYnLVEQJpAm1TVqlappN9lU9ev3Bvg/edit?usp=sharing). You will need test Courtesy Card credentials and test Littlepay card credentials.
1. Click **Ayuda** in the footer to review the Help page.
1. Jot down any issues or notes during the review. Highlight any proposed changes on the **forTranslation** tab in the [Cal-ITP Benefits Application Copy](https://docs.google.com/spreadsheets/d/1_Gi_YbJr4ZuXCOsnOWaewvHqUO1nC1nKqiVDHvw0118/edit?usp=sharing) spreadsheet. Use the comment feature in Google Sheets to share your feedback. Please mention Andy Walker and Machiko Yasuda in each comment.
