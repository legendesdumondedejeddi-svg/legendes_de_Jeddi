// netlify/functions/donate.js
exports.handler = async function(event, context) {
  // PAYPAL_BUSINESS doit être configurée dans Netlify (Dashboard > Site settings > Build & deploy > Environment)
  const paypal = process.env.PAYPAL_BUSINESS || "";
  if (!paypal) {
    return {
      statusCode: 500,
      body: "Service indisponible. PAYPAL_BUSINESS non configurée."
    };
  }

  // Construire l'URL PayPal. Ici j'utilise la route donate via email (PayPal standard)
  // Tu peux remplacer par ton bouton hosted_id si tu as un hosted_button_id.
  const params = new URLSearchParams({
    business: paypal,
    currency_code: "EUR",
    // amount: "5.00" // optionnel : tu peux supprimer ou fixer
  });
  const url = `https://www.paypal.com/donate?${params.toString()}`;

  return {
    statusCode: 302,
    headers: {
      Location: url
    },
    body: "" // redirect
  };
};

