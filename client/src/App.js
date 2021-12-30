import logo from "./images/logo.svg";
import logopng from "./images/logo512.png";
import "./App.css";
import { Button, Typography } from "@mui/material";
import useRouter from "./hooks/useRouter";
import GradesSheet from "./GradesSheet";
import BubblesSheet from "./BubblesSheet";
function App() {
  const router = useRouter();
  const tabs = [
    { name: "Grades sheet", query: "grades" },
    { name: "Bubble sheet correction", query: "bubble" },
  ];
  console.log();
  return (
    <div className="App">
      <img src={logopng} className="App-logo" alt="logo" />
      {!router.query.tab && (
        <Typography fontWeight={900} color="secondary" variant="h6" component="body">
          Fill out grades or grade bubble sheets
        </Typography>
      )}
      <div className="home-tabs">
        {tabs.map((tab, index) => (
          <Button
            key={index}
            sx={{ margin: "16px", minWidth: "250px" }}
            variant="contained"
            onClick={() => router?.push(`/?tab=${tab.query}`)}
            color={router.query.tab === tab.query ? "primary" : "inherit"}
          >
            {tab.name}
          </Button>
        ))}
      </div>
      {router.query.tab && (
        <div>{router.query.tab === "grades" ? <GradesSheet /> : <BubblesSheet />}</div>
      )}
    </div>
  );
}

export default App;
