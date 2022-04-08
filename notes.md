For environment variables on linux, use environment.d. This will only be available on systemd systems, but it's the best option. Apparently works similar to Windows environment variables.

Let b-fuze (Mike32)#9778 on Ubuntu Hideout know if you can update variables without logging in/out.

For adding package type definitions install them as a `package-typedef` package. Store the files in `package-types` next to `config.json`.

`latest-stable` and `latest` are defined in package.acp.

Add check in `install` to make sure `latest-stable` and `latest` reference versions defined in the package.