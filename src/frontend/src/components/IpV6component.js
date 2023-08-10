import React, { useState, useMemo, useEffect } from "react";
import {
  //LineChart,
  //Line,
  //XAxis,
  //YAxis,
  //CartesianGrid,
  //Tooltip,
  //Legend,
  //ResponsiveContainer,
} from "recharts";
import { Container, Row, Form, Button, Col, Spinner } from "react-bootstrap";
import countryList from "react-select-country-list";
import {
  LineChartGraphBody,
  DatesCountryForm,
} from "./DnsGraph.js";
import { geojson } from "./geo_data.js";

export const get_current_date = () => new Date().toISOString().split("T")[0];
export const get_n_days_ago_from_current_date = (n) => {
  let date = new Date();
  date.setDate(date.getDate() - n);
  return date.toISOString().split("T")[0];
};
export const get_n_days_ago_from_given_date = (date, n) => {
  // date in the format of YYYY-MM-DD
  let date_obj = new Date(date);
  date_obj.setDate(date_obj.getDate() - n);
  return date_obj.toISOString().split("T")[0];
};
{/*
const DateTimeCountryForm = ({ updateData, initialData }) => {
  const handleSubmit = (event) => {
    event.preventDefault();
    const date1 = new Date(event.target.date1.value);
    const date2 = new Date(event.target.date2.value);
    const today = new Date();

    // set the hours, minutes, seconds and milliseconds to 0 to compare only the date part
    today.setHours(0, 0, 0, 0);
    date1.setHours(0, 0, 0, 0);
    date2.setHours(0, 0, 0, 0);

    if (date1 > today || date2 > today) {
      alert("Selected dates cannot be in the future!");
      return;
    }

    updateData({
      date1: event.target.date1.value,
      date2: event.target.date2.value,
      country: event.target.country.value,
    });
  };

  const country_options = useMemo(() => countryList().getData(), []);
  return (
    <Form onSubmit={handleSubmit}>
      <Container>
        <Row className="d-flex justify-content-center align-items-end">
          <Col md={3}>
            <Form.Group controlId="date1">
              <Form.Label>Reference Date</Form.Label>
              <Form.Control type="date" defaultValue={initialData["date1"]} />
            </Form.Group>
          </Col>
          <Col md={3}>
            <Form.Group controlId="date2">
              <Form.Label>Compare Date</Form.Label>
              <Form.Control type="date" defaultValue={initialData["date2"]} />
            </Form.Group>
          </Col>
          <Col md={3}>
            <Form.Group controlId="country">
              <Form.Label>Country</Form.Label>
              <Form.Select defaultValue={initialData["country"]}>
                {country_options.map((country) => (
                  <option key={country.value} value={country.value}>
                    {country.label}
                  </option>
                ))}
              </Form.Select>
            </Form.Group>
          </Col>
          <Col md={1} className="d-flex align-items-end justify-content-center">
            <Button variant="primary" type="submit">
              Submit
            </Button>
          </Col>
        </Row>
      </Container>
    </Form>
  );
};
*/}
{/*const LineIPv6Graph = ({ data }) => {
  return (
    <ResponsiveContainer width="100%">
      <LineChart
        data={data}
        margin={{
          top: 10,
          bottom: 10,
        }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis domain={[0, 100]} />
        <Tooltip />
        <Legend />
        <Line
          type="monotone"
          dataKey="ipv6"
          stroke="#8884d8"
          activeDot={{ r: 8 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};
*/}

{/*const IpV6Controller = () => {
  const [data, setData] = useState([]);

  const computeInitialData = () => {
    return {
      date1: get_n_days_ago_from_current_date(30),
      date2: get_current_date(),
      country: "IL",
    };
  };
  const [dates_country_data, updateData] = useState(computeInitialData());
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const country_code = dates_country_data["country"];
        const first_date = dates_country_data["date1"];
        const second_date = dates_country_data["date2"];
        setIsLoading(true);
        const response = await fetch(
          `/ipv/country=${country_code}&first_date=${first_date}&second_date=${second_date}`
        );
        const jsonData = await response.json();
        setData(jsonData.data);
        // setData([]);
        setIsLoading(false);
      } catch (error) {
        console.log(error.message);
      }
    };
    fetchData();
  }, [dates_country_data]);

  const render_conent = () => {
    if (!isLoading) {
      if (data.length > 0) {
        return (
          <Col
            md={12}
            style={{
              marginTop: "10px",
              height: "75vh",
              border: "1px solid black",
              borderRadius: "10px",
            }}
          >
            <LineIPv6Graph data={data} />
          </Col>
        );
      } else {
        // case where there is no data
        return <Col>no data found at server</Col>;
      }
    } else if (isLoading) {
      return <LoadingSpinner />;
    }
  };
  return (
    <Container>
      <Row className="justify-content-md=center">{render_conent()}</Row>
      <Row>
        <Col md={12}>
          <DateTimeCountryForm
            updateData={updateData}
            initialData={computeInitialData()}
          />
        </Col>
      </Row>
    </Container>
  );
};*/}

const IpV6Controller = () => {
  const [country_code, setCountryCode] = useState("ISR");
  const [country_chart_date, setCountryChartDate] = useState(
    get_current_date()
  );
  //Need mode for using DNSLifeChartGraphBody function
  const [mode, changeMode] = useState("whole_world");
  const geo_options = useMemo(
    () =>
      geojson.objects.world.geometries.map((item) => {
        return { value: item.id, label: item.properties.name };
      }),
    []
  );
  const [state, setState] = useState({
    data: [],
    startDate: get_n_days_ago_from_given_date(country_chart_date, 2),
    endDate: country_chart_date,
    countries: [geo_options.find((item) => item.value == country_code)],
  });
  const setIsLoadingState = (loadingState) => {
    setState({ ...state, isLoading: loadingState });
  };
  const updateData = (newData) => {
    setState({ ...state, data: newData });
  };
  const updateSelectedCountries = (newCountries) => {
    setState({ ...state, countries: newCountries });
  };
  const updateDates = (newStartDate, newEndDate) => {
    setState({ ...state, startDate: newStartDate, endDate: newEndDate });
  };
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoadingState(true);
        console.log("real loading")
        //TODO: check if I can use state.countries this way!
        const country_code = state.countries;
        const first_date = state.startDate;
        const second_date = state.endDate;
        const response = await fetch(
          `/ipv/country=${country_code}&first_date=${first_date}&second_date=${second_date}`
        );
        const jsonData = await response.json();
        setIsLoadingState(false);
        updateData(jsonData.data);
      } catch (error) {
        console.log(error.message);
      }
    };
    fetchData();
  }, [state.startDate, state.endDate, state.countries]);
  return (
    <Container>
      {!state.isLoading ? (
        <React.Fragment>
          <Row>
            <LineChartGraphBody
              state={state}
              changeMode={changeMode}
              setCountryChartDate={setCountryChartDate}
            />
          </Row>
          <DatesCountryForm
            updateDates={updateDates}
            updateSelectedCountries={updateSelectedCountries}
            state={state}
            geo_options={geo_options}
          />
        </React.Fragment>
      ) : (
        <LoadingSpinner />
      )}
    </Container>
  );
};

export function LoadingSpinner() {
  return (
    <div
      className="d-flex justify-content-center align-items-center"
      style={{ height: "75vh" }}
    >
      <Spinner animation="border" role="status">
        <span className="visually-hidden">Loading...</span>
      </Spinner>
    </div>
  );
}
const IpV6component = () => {
  return <IpV6Controller />;
};

export default IpV6component;
