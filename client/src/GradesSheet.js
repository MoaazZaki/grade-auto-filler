import { Button, CircularProgress, Typography } from "@mui/material";
import { Box } from "@mui/system";
import React, { useState } from "react";
import ImageUpload from "./ImageUpload";
import axios from "axios";
import Progress from "./Progress";
import { Download, Done } from "@mui/icons-material";
import CustomAlert from "./CustomAlert";

axios.defaults.baseURL = process.env.REACT_APP_BASE_URL;

export default function GradesSheet() {
  const initialImageState = {
    mainState: "initial", // initial, search, gallery, uploaded
    imageUploaded: 0,
    selectedFile: null,
    searchURL: "",
  };
  const [imageState, setImageState] = useState(initialImageState);
  const [csvURL, setCsvURL] = useState(null);
  const [percentCompleted, setPercentCompleted] = useState(null);
  const [imageFile, setImagefile] = useState(null);
  const [openAlert, setOpenAlert] = React.useState(false);
  return (
    <div>
      <ImageUpload
        Name="Input Image"
        imageState={imageState}
        setImageState={setImageState}
        getTheImage={(image) => {
          setCsvURL(null);
          setImagefile(image);
        }}
      />
      {Boolean(imageState.imageUploaded) && (
        <Box m={2}>
          <Box>
            <Button
              onClick={async () => {
                let res = null;
                var formData = new FormData();
                formData.append("files[]", imageFile);
                try {
                  console.log("hello");
                  setCsvURL(null);
                  res = await axios.post(
                    "/grades",
                    // {
                    //   "files[]": imageState.selectedFile,
                    // },
                    formData,
                    {
                      headers: {
                        "Content-Type": "multipart/form-data",
                      },
                      onUploadProgress: (progressEvent) => {
                        console.log(progressEvent);
                        console.log(progressEvent.currentTarget);
                        console.log(progressEvent.currentTarget.responseHeaders);
                        // const total = parseFloat(
                        //   progressEvent.currentTarget.responseHeaders["Content-Length"]
                        // );
                        // const current = progressEvent.currentTarget.response.length;
                        // let percentCompleted = Math.floor((current / total) * 100);
                        // console.log("completed: ", percentCompleted);

                        console.log(progressEvent.loaded / progressEvent.total);
                        setPercentCompleted(
                          Math.floor((progressEvent.loaded / progressEvent.total) * 100)
                        );
                      },
                    }
                  );
                  setPercentCompleted(null);
                  setCsvURL(res.data.excelFile);
                  setImageState(initialImageState);
                } catch (err) {
                  console.log(err);
                  setPercentCompleted(null);
                  setOpenAlert(true);
                }
              }}
              variant="contained"
              color={percentCompleted !== null ? "inherit" : "secondary"}
              disabled={percentCompleted !== null}
              // endIcon={percentCompleted !== null ? <Progress progress={percentCompleted} /> : null}
            >
              Convert to csv
            </Button>
          </Box>

          {percentCompleted !== null && (
            <>
              <CircularProgress sx={{ marginBlock: "8px" }} />
              <Typography fontWeight={700} color="#8f8f8f">
                Please be patient
              </Typography>
            </>
          )}
        </Box>
      )}
      {csvURL && (
        <Box p={2}>
          <Typography pb={1} color="#8f8f8f" fontWeight={700}>
            Conversion finished
            <Done sx={{ verticalAlign: "middle", marginInlineStart: "8px" }} />
          </Typography>
          <Button
            color="success"
            variant="outlined"
            onClick={() => {
              window.open(csvURL);
            }}
            endIcon={<Download />}
          >
            Download CSV
          </Button>
        </Box>
      )}
      <CustomAlert
        message={
          "Oops! Something went wrong from the server side :( Perhaps you could try another photo."
        }
        open={openAlert}
        setOpen={setOpenAlert}
      />
    </div>
  );
}
