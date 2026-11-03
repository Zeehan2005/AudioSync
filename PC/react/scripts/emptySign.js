// No-op Windows code signer.
// electron-builder only downloads the winCodeSign helper (which needs
// symlink/Developer-Mode privileges) when it plans to sign with its built-in
// signer. Providing this custom (empty) signer makes electron-builder skip
// that download entirely, so we can produce an UNSIGNED installer in
// environments without admin rights. Replace with a real signing script to
// ship a signed build.
module.exports = async function emptySign(/* configuration */) {
  return;
};
