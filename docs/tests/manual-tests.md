# Manual tests

This page lists manual testing scripts for various flows.

## Getting started: Using test credentials

In order to fully test the app, you will need to use test credentials, which are available here: [Benefits Test Data](https://docs.google.com/document/d/1bFynuiLy9POXYEYnLVEQJpAm1TVqlappN9lU9ev3Bvg/edit?usp=sharing).

> **Important**: Please do not use your personal accounts for Login.gov, ID.me, etc. to complete your review.

### Login.gov and Veteran Confirmation API

To test the Login.gov (Older adult) and Veteran Confirmation API (Veteran) enrollment pathway flows, you will need an e-mail address, a real cell phone and test account `yml` files from the [Benefits Test Data document](https://docs.google.com/document/d/1bFynuiLy9POXYEYnLVEQJpAm1TVqlappN9lU9ev3Bvg/edit#heading=h.t61g222qmr19).

Read [the Login.gov Testing identity proofing documentation](https://developers.login.gov/testing/#testing-identity-proofing) for complete instructions. In summary, once you click **Get started with Login.gov**, follow these instructions:

1. Before you get started, download the `proofing-senior.yml` (or any other `yml` file for the specific user you are testing) from the [Benefits Test Data document](https://docs.google.com/document/d/1bFynuiLy9POXYEYnLVEQJpAm1TVqlappN9lU9ev3Bvg/edit#heading=h.t61g222qmr19). For example, if you are testing the Veteran flow, or a non-senior flow, download the `proofing-veteran.yml` or `proofing-nonsenior.yml` files respectively.
1. Click **Create an account**.
1. Create a test email address, like `yourname+older_adult@compiler.la`. [Gmail supports adding suffixes to your email address](https://support.google.com/a/users/answer/9282734?visit_id=638381024326725285-629188737&rd=1#email-address-variation).
1. Select **English (default)** and check **I read and accept the Login.gov Rules of Use**.
1. Check your email for a confirmation link and click it.
1. Go through the password and authentication method setup flows. Make sure to select **Text or voice message**. Selecting **Backup codes** is useful if you plan to use this account again. Make sure to save your password, as you will need to enter it at the very end.
1. Enter your real cell phone number.
1. Check your text messages for a message from Login.gov. The message should specify `idp.int.identitysandbox.gov`.
1. Enter the code into the browser.
1. Save the backup codes, if selected.
1. Click **Continue** until you reach the `How would you like to add your ID?` part of the flow.
1. Click **Upload photos**.
1. Upload the `.yml` files you downloaded in the first step for both the front and back of the ID. Click **Continue**.
1. For **Enter your Social Security number**, enter a number that starts with `900` or `666`. **DO NOT ENTER YOUR PERSONAL SOCIAL SECURITY NUMBER.**
1. At this point, the **Verify your information** page should show the data you have in the `.yml` file you uploaded. Double-check that the age (date of birth) is accurate.
1. Verify your phone again.
1. Re-enter your password. You should be redirected back to the Benefits application.

### Agency cards

To test the agency card enrollment pathway, use the following test credentials:

- [Courtesy Cards (MST)](https://docs.google.com/document/d/1bFynuiLy9POXYEYnLVEQJpAm1TVqlappN9lU9ev3Bvg/edit#heading=h.l2jcqsl4s6rh)
- [Mobility Pass (SBMTD)](https://docs.google.com/document/d/1bFynuiLy9POXYEYnLVEQJpAm1TVqlappN9lU9ev3Bvg/edit#heading=h.rkuhoc19aku7)

### Littlepay

To test the Littlepay card enrollment flow, use the test Visa credentials in the [Benefits Test Data document](https://docs.google.com/document/d/1bFynuiLy9POXYEYnLVEQJpAm1TVqlappN9lU9ev3Bvg/edit#heading=h.6l8f6lihq1vz), along with any fake name, any CVV and an expiration date in the future.

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
