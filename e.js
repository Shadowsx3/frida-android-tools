console.log("Script loaded successfully");
Java.deoptimizeEverything()

function hookAuth(idToken, accessToken, refreshToken) {
    Java.perform(function () {
            console.log("[ * ] Starting implementation override...");
            console.log("Setting credentials with tokens:");
            console.log("ID Token: " + idToken);
            console.log("Access Token: " + accessToken);
            console.log("Refresh Token: " + refreshToken);

            let Credentials = Java.use("com.auth0.android.result.Credentials");
            let Date = Java.use('java.util.Date');

            let currentDate = Date.$new();
            let expiresAt = Date.$new(currentDate.getTime() + 900000);

            let credentials = Credentials.$new(
                idToken,           // idToken passed from Python
                accessToken,       // accessToken passed from Python
                "Bearer",          // type
                refreshToken,      // refreshToken passed from Python
                expiresAt,         // expiresAt set to 15 minutes from now
                "openid profile email offline_access"  // scope
            );

            console.log("Credentials object created: " + credentials.toString());

            let SecureCredentialsManager = Java.use("com.auth0.android.authentication.storage.SecureCredentialsManager");
            SecureCredentialsManager["saveCredentials"].implementation = function (credentials) {
                    console.log(`SecureCredentialsManager.saveCredentials is called: credentials=${credentials}`);
                    this["saveCredentials"](credentials);
            };

            console.log("Save hook set");

            let classFound = false;

            Java.choose("com.auth0.android.authentication.storage.SecureCredentialsManager", {
                   onMatch: function (instance) {
                        if (!classFound) {
                            console.log("Found SecureCredentials instance");
                            classFound = true
                            instance["saveCredentials"](credentials);
                        }
                   },
                   onComplete: function () {}
            });
    });
}

rpc.exports = {
    setcredentials: hookAuth
};
