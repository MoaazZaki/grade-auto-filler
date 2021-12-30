import { Article, Grading, PictureAsPdf } from "@mui/icons-material";
import {
  Button,
  Checkbox,
  Chip,
  Container,
  FormControl,
  FormControlLabel,
  FormGroup,
  InputLabel,
  MenuItem,
  Radio,
  RadioGroup,
  Select,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import axios from "axios";
import React from "react";
import CustomAlert from "./CustomAlert";
import ImageUpload from "./ImageUpload";
axios.defaults.baseURL = process.env.REACT_APP_BASE_URL;

export default function BubblesSheet() {
  //States
  const [modelAnswerMode, setModelAnswerMode] = React.useState(false);
  const [numberOfChoices, setNumberOfChoices] = React.useState(3);
  const [numberOfQuestions, setNumberOfQuestions] = React.useState(20);
  const [wrongAnswerGrade, setWrongAnswerGrade] = React.useState(1);
  const [allowMultiAnswers, setAllowMultiAnswers] = React.useState(false);
  const [allowNegativeGrades, setAllowNegativeGrades] = React.useState(false);
  const [questionsQrades, setQuestionsQrades] = React.useState(Array(numberOfQuestions).fill(1));
  const [numberOfIdDigits, setNumberOfIdDigits] = React.useState(5);
  const [questionsCheckBoxChoices, setQuestionsCheckBoxChoices] = React.useState(
    Array(numberOfQuestions)
      .fill(Array(numberOfChoices).fill(false))
      .map((_) =>
        Array(numberOfChoices)
          .fill(false)
          .map((_, index) => (index === 0 ? true : false))
      )
  );

  const [questionsRadioButtonChoices, setQuestionsRadioButtonChoices] = React.useState(
    Array(numberOfQuestions).fill(0)
  );

  //Image State
  const initialImageState = {
    mainState: "initial", // initial, search, gallery, uploaded
    imageUploaded: 0,
    selectedFile: null,
    searchURL: "",
  };
  const [imageState, setImageState] = React.useState(initialImageState);
  const [imageFile, setImagefile] = React.useState(null);

  //Some needed constants
  const choiceLetter = ["A", "B", "C", "D", "E"];
  const choiceLetterLower = ["a", "b", "c", "d", "e"];

  //For error alerts
  const [openAlert, setOpenAlert] = React.useState(false);
  const [openAlertImageError, setOpenAlertImageError] = React.useState(false);

  //For outputing the final grade and paper
  const [finalGrade, setFinalGrade] = React.useState(undefined);
  const [finalPaper, setFinalPaper] = React.useState(undefined);

  //Loading state
  const [isLoadingGrade, setIsLoadingGrade] = React.useState(false);
  const [isLoadingPaper, setIsLoadingPaper] = React.useState(false);

  //check box choice
  const CheckBoxChoice = ({ index }) => {
    return (
      <FormGroup key={index}>
        <div style={{ display: "flex", justifyContent: "center" }}>
          {Array(numberOfChoices)
            .fill(0)
            .map((_, choiceIndex) => {
              return (
                <FormControlLabel
                  key={choiceIndex}
                  control={
                    <Checkbox
                      checked={
                        questionsCheckBoxChoices[index]
                          ? questionsCheckBoxChoices[index][choiceIndex]
                          : false
                      }
                      onChange={(e) => {
                        setQuestionsCheckBoxChoices((prev) =>
                          prev.map((el, elIndex) =>
                            el.map((elInner, elInnerIndex) =>
                              elIndex === index && elInnerIndex === choiceIndex
                                ? e.target.checked
                                : elInner
                            )
                          )
                        );
                      }}
                      inputProps={{ "aria-label": "controlled" }}
                    />
                  }
                  label={choiceLetter[choiceIndex]}
                />
              );
            })}
        </div>
      </FormGroup>
    );
  };
  //end of check box choice

  //Effects
  React.useEffect(() => {
    setQuestionsRadioButtonChoices(Array(numberOfQuestions).fill(0));
    setQuestionsCheckBoxChoices(
      Array(numberOfQuestions)
        .fill(Array(numberOfChoices).fill(false))
        .map((_) =>
          Array(numberOfChoices)
            .fill(false)
            .map((_, index) => (index === 0 ? true : false))
        )
    );
  }, [numberOfChoices, numberOfQuestions]);

  //radio button choice
  const RadioButtonChoice = ({ index }) => {
    return (
      <FormControl key={index}>
        <RadioGroup
          value={questionsRadioButtonChoices[index] ?? 0}
          onChange={(e) => {
            setQuestionsRadioButtonChoices((prev) =>
              prev.map((ele, eleIndex) => (eleIndex === index ? +e.target.value : ele))
            );
          }}
        >
          <div style={{ display: "flex", justifyContent: "center" }}>
            {Array(numberOfChoices)
              .fill(0)
              .map((_, choiceIndex) => {
                return (
                  <FormControlLabel
                    key={choiceIndex}
                    value={choiceIndex}
                    control={<Radio />}
                    label={choiceLetter[choiceIndex]}
                  />
                );
              })}
          </div>
        </RadioGroup>
      </FormControl>
    );
  };
  //end of radio button choice

  //question wrapper
  const QuestionWarpper = ({ index, Comp }) => {
    return (
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
        }}
        key={index}
      >
        <Typography>{`Question ${index + 1}`}</Typography>
        <Comp index={index} />
        <TextField
          value={questionsQrades[index] ?? 1}
          onChange={(e) => {
            setQuestionsQrades((prev) =>
              prev.map((el, elIndex) => (elIndex === index ? +e.target.value : el))
            );
          }}
          label="Question grade"
          type="number"
          sx={{ width: "150px" }}
        />
      </div>
    );
  };
  //end of question wrapper
  const NumberOfQuestionsField = (
    <TextField
      label="Number of questions (from 1 up to 45)"
      placeholder="minimum is 1 and maximum is 45"
      type="number"
      fullWidth
      value={numberOfQuestions}
      onChange={(e) => {
        const intE = +e.target.value;
        if (intE <= 45 && intE >= 1) setNumberOfQuestions(intE);
      }}
      InputProps={{
        inputProps: {
          max: 45,
          min: 1,
        },
      }}
    />
  );
  const NumberOfChoicesField = (
    <TextField
      label="Number of choices of each question (from 2 up to 5)"
      placeholder="minimum is 2 and maximum is 5"
      type="number"
      fullWidth
      value={numberOfChoices}
      onChange={(e) => {
        const intE = +e.target.value;
        if (intE <= 5 && intE >= 2) setNumberOfChoices(intE);
      }}
      InputProps={{
        inputProps: {
          max: 5,
          min: 2,
        },
      }}
    />
  );

  return (
    <React.Fragment>
      <Container maxWidth="md" sx={{ paddingBlock: "32px" }}>
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            flexWrap: "wrap",
          }}
        >
          <Button
            color={"secondary"}
            onClick={() => setModelAnswerMode(false)}
            sx={{ width: "250px", height: "100px", marginBlockEnd: "32px", borderRadius: "0px" }}
            startIcon={<Article />}
            variant={modelAnswerMode ? "outlined" : "contained"}
          >
            Make your exam paper
          </Button>
          <Button
            color={"secondary"}
            onClick={() => setModelAnswerMode(true)}
            sx={{ width: "250px", height: "100px", marginBlockEnd: "32px", borderRadius: "0px" }}
            startIcon={<Grading />}
            variant={modelAnswerMode ? "contained" : "outlined"}
          >
            Grade a paper based on a model answer
          </Button>
        </div>
        <form>
          {modelAnswerMode ? (
            <Stack spacing={2}>
              {/* Number of questions  */}
              {NumberOfQuestionsField}
              {/* Number of choices  */}
              {NumberOfChoicesField}
              {/* Wrong answer grade */}
              <TextField
                label="Wrong answer grade"
                type="number"
                fullWidth
                value={wrongAnswerGrade}
                onChange={(e) => setWrongAnswerGrade(+e.target.value)}
                InputProps={{
                  inputProps: {
                    min: 0,
                  },
                }}
              />
              {/* Allow multi answers checkbox */}
              <FormGroup>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={allowMultiAnswers}
                      onChange={(e) => setAllowMultiAnswers(e.target.checked)}
                      inputProps={{ "aria-label": "controlled" }}
                    />
                  }
                  label="Allow multi answers"
                />
              </FormGroup>

              {/* Allow multi answers checkbox */}
              <FormGroup>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={allowNegativeGrades}
                      onChange={(e) => setAllowNegativeGrades(e.target.checked)}
                      inputProps={{ "aria-label": "controlled" }}
                    />
                  }
                  label="Allow negative grades"
                />
              </FormGroup>
              {Array(numberOfQuestions)
                .fill(0)
                .map((_, index) => {
                  return allowMultiAnswers ? (
                    <QuestionWarpper key={index} index={index} Comp={CheckBoxChoice} />
                  ) : (
                    <QuestionWarpper key={index} index={index} Comp={RadioButtonChoice} />
                  );
                })}
              <Typography color="GrayText">
                {Boolean(imageState.imageUploaded)
                  ? "Thank you for uploading!"
                  : "Please upload the paper you want to grade"}
              </Typography>
              <ImageUpload
                Name="Input Image"
                imageState={imageState}
                setImageState={setImageState}
                getTheImage={(image) => {
                  setImagefile(image);
                }}
              />
              {finalGrade && (
                <Typography my={2} fontWeight={700}>
                  The grade is:{" "}
                  <Chip color="secondary" size="large" label={finalGrade} component="span" />
                </Typography>
              )}
              <Button
                disabled={isLoadingGrade}
                color={isLoadingGrade ? "inherit" : "primary"}
                onClick={async (e) => {
                  e.preventDefault();
                  if (!Boolean(imageState.imageUploaded)) return setOpenAlertImageError(true);
                  try {
                    setIsLoadingGrade(true);
                    var formData = new FormData();
                    formData.append("numberOfChoices", numberOfChoices);
                    formData.append("numberOfQuestions", numberOfQuestions);
                    formData.append("wrongAnswerGrade", wrongAnswerGrade);
                    formData.append("allowMultiAnswers", allowMultiAnswers);
                    formData.append("allowNegativeGrades", allowNegativeGrades);
                    formData.append("questionsQrades", JSON.stringify(questionsQrades));
                    formData.append(
                      "answers",
                      allowMultiAnswers
                        ? JSON.stringify(
                            questionsCheckBoxChoices.map((el) => {
                              const choicesL = [];
                              for (let i = 0; i < el.length; i++)
                                if (el[i]) choicesL.push(choiceLetterLower[i]);

                              return choicesL?.length === 0
                                ? choiceLetterLower[0] //if no choice slected default is 'a'
                                : choicesL?.length === 1
                                ? choicesL[0] //if only one choice selected make it a string
                                : choicesL; //more than one value send it as array
                            })
                          )
                        : JSON.stringify(
                            questionsRadioButtonChoices.map((el) => choiceLetterLower[el])
                          )
                    );
                    formData.append("files[]", imageFile);

                    const res = await axios.post("/bubble/grade", formData);
                    setFinalGrade(res.data.grade);
                  } catch (err) {
                    setOpenAlert(true);
                  } finally {
                    setIsLoadingGrade(false);
                  }
                }}
                variant="contained"
                type="submit"
              >
                Grade Paper
              </Button>
            </Stack>
          ) : (
            <Stack spacing={2}>
              {NumberOfQuestionsField}
              {NumberOfChoicesField}
              <FormControl fullWidth>
                <InputLabel>Number of digits in the student's ID</InputLabel>
                <Select
                  variant="standard"
                  onChange={(e) => setNumberOfIdDigits(+e.target.value)}
                  value={numberOfIdDigits}
                >
                  {[1, 2, 3, 4, 5, 6, 7].map((el) => (
                    <MenuItem value={el} key={el}>
                      {el}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              {finalPaper && (
                <Button
                  onClick={() => {
                    window.open(finalPaper);
                  }}
                  color="error"
                  variant="outlined"
                  startIcon={<PictureAsPdf />}
                >
                  Download paper
                </Button>
              )}
              <Button
                disabled={isLoadingPaper}
                color={isLoadingPaper ? "inherit" : "primary"}
                onClick={async (e) => {
                  e.preventDefault();
                  try {
                    setIsLoadingPaper(true);
                    const res = await axios.post("/bubble/paper", {
                      numberOfChoices,
                      numberOfQuestions,
                      numberOfIdDigits,
                    });
                    setFinalPaper(res.data.paper);
                  } catch (err) {
                    setOpenAlert(true);
                  } finally {
                    setIsLoadingPaper(false);
                  }
                }}
                variant="contained"
                type="submit"
              >
                Generate an exam paper
              </Button>
            </Stack>
          )}
        </form>
      </Container>
      <CustomAlert
        message={"Oops! Something went wrong from the server side."}
        open={openAlert}
        setOpen={setOpenAlert}
      />
      <CustomAlert
        message={"Please upload the image you want to grade first"}
        open={openAlertImageError}
        setOpen={setOpenAlertImageError}
      />
    </React.Fragment>
  );
}
