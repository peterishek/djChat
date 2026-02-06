import { createTheme } from "@mui/material";

declare module "@mui/material/styles" {
    interface Theme {
        primaryAppBar: {
            height: number ;
        };
    }
    interface ThemeOptions {
        primaryAppBar: {
            height: number
        };
    }
}

export const createMuiTheme = () => {
    let theme = createTheme({
        primaryAppBar: {
            height: 50,
        }
    });
    return theme;
};

export default createMuiTheme