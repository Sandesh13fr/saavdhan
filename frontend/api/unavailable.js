// Used only until the encrypted AWS backend can be provisioned.
export default function handler(_request, response) {
  response.setHeader('Cache-Control', 'no-store');
  response.status(503).json({detail: 'The workspace service is temporarily unavailable while AWS hosting is being completed. Please try again later.'});
}
