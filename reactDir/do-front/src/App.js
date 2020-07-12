import React from 'react';

import DatePicker from "react-datepicker";

import 'react-dates/lib/css/_datepicker.css';
import 'react-dates/initialize';
import {DateRangePicker, SingleDatePicker, DayPickerRangeController } from 'react-dates';

import {Tab, TabList, TabPanel, Tabs} from 'react-tabs';
import 'react-tabs/style/react-tabs.css';

import "react-datepicker/dist/react-datepicker.css";
import './App.css';


function App() {
    return (
        <div className="App">
            {/*<header className="App-header">*/}
            {/*<img src={logo} className="App-logo" alt="logo" />*/}

        <Tabs>
            <TabList>
                <Tab>List of donations</Tab>
                <Tab>Download a dump</Tab>
            </TabList>

            <TabPanel>
                <section className="donations-list">
                    <ListElem/>
                </section>
                <aside className="filter">
                    <FilterField/>
                    <FilterDataField/>
                </aside>
            </TabPanel>
            <TabPanel>
                <ArchiveGetter/>
            </TabPanel>
        </Tabs>
            {/*</header>*/}
        </div>
    )
}


class FilterDataField extends React.Component{
    constructor() {
        super();
        updateFilterVal = updateFilterVal.bind(this)
        this.state = {
            startDate: null,
            endDate: null
        };
    }


    handleChange = (id, date) => {
        console.log(id, date);
        if(id === "startDate"){
            this.setState({
                startDate: date
            });
            updateFilterVal("startDate", date)
        }
        if(id === "endDate"){
            this.setState({
                endDate: date
            });
            updateFilterVal("endDate", date)
        }
    };

    render() {
        return (
            <div className="dateFilter">
                <div style={{alignSelf: "center"}}>Filtering by date:</div>
                <DateRangePicker style={{fontSize: "small"}}
                    startDatePlaceholderText="start point"
                    endDatePlaceholderText="end point"
                    isOutsideRange={() => false}
                    startDate={this.state.startDate} // momentPropTypes.momentObj or null,
                    startDateId="your_unique_start_date_id" // PropTypes.string.isRequired,
                    endDate={this.state.endDate} // momentPropTypes.momentObj or null,
                    endDateId="your_unique_end_date_id" // PropTypes.string.isRequired,
                    onDatesChange={({ startDate, endDate }) => {this.handleChange("startDate", startDate, endDate); this.handleChange("endDate", endDate)}} // PropTypes.func.isRequired,
                    focusedInput={this.state.focusedInput} // PropTypes.oneOf([START_DATE, END_DATE]) or null,
                    onFocusChange={focusedInput => this.setState({ focusedInput })} // PropTypes.func.isRequired,
                />
            </div>
        )
    }
}


function updateFilterVal(key, newValue){
    if(key === "filterText")
        this.setState({filterText: newValue})

    if(key === "startDate")
        this.setState({startDate: newValue})

    if(key === "endDate")
        this.setState({endDate: newValue})
}


class FilterField extends React.Component{
    constructor(props){
        super(props);
        this.state = {filterText: ""}
    }

    handleChange(event) {
        this.setState({filterText: event.target.value});
        updateFilterVal("filterText", event.target.value)
    }

    render() {
        return (
            <div>
                Filter by contents of email and city:
                <input type="text" value={this.state.filterText} onChange={(e) => this.handleChange(e)}/>
            </div>
        );
    }
}


class ArchiveGetter extends React.Component{

    downloadDump = () => {
          // fake server request, getting the file url as response
        setTimeout(() => {
            const fd = this.state.startDate
            const td = this.state.endDate
            const response = {
                file: "/download?from="+ ("0"+fd.getDate()).slice(-2)+("0"+(fd.getMonth()+1)).slice(-2)+fd.getFullYear() +
                    "&to="+ ("0"+td.getDate()).slice(-2)+("0"+(td.getMonth()+1)).slice(-2)+td.getFullYear(),
            };
            // server sent the url to the file!
            // now, let's download:
            window.open(response.file);
            // you could also do:
            // window.location.href = response.file;
        }, 100);
    }

    state = {
        startDate: new Date(),
        endDate: new Date()
    };

    handleChange = (id, date) => {
        if(id === "startDate"){
            this.setState({
                startDate: date
            });
        }
        if(id === "endDate"){
            this.setState({
                endDate: date
            });
        }
    };

    render() {
        return (
            <div>
                Get archive entries by date
                <br/>
                From:
                <DatePicker
                    dateFormat="dd/MM/yyyy"
                    selected={this.state.startDate}
                    onChange={(date) => this.handleChange("startDate", date)}
                    showYearDropdown
                    showMonthDropdown
                />
                <br/>
                To:
                <DatePicker
                    dateFormat="dd/MM/yyyy"
                    selected={this.state.endDate}
                    onChange={(date) => this.handleChange("endDate", date)}
                    showYearDropdown
                    showMonthDropdown
                />
                <br/>
                <button onClick={this.downloadDump}>
                    click me
                </button>
            </div>
        )
    }
}


class ListElem extends React.Component {
    componentDidMount() {
    fetch("/api/getList"
    )
        .then(res => res.json())
        .then(
        (result) => {
            this.setState({
                isLoaded: true,
                items: result.items,
                donationsPDay: result.donations_per_day,
                filterText: ""
            });
        },
        // Note: it's important to handle errors here
        // instead of a catch() block so that we don't swallow
        // exceptions from actual bugs in components.
        (error) => {
            this.setState({
                isLoaded: true,
                filterText: "",
                error
            });
        }
      )
    }


    constructor(props) {
        super(props);
        this.state = {
            items: [[3093, "15.03.2020", "14:43:56", "tchurovtim@2gmail.com", "Санкт-Петербург", "200"], [2, "15.03.2020", "14:43:56", "tchurovtim@gmail.com", "Санкт-Петербург", "200"]],
            donationsPDay: {"15.03.2020": {"donations_that_day": 2,
                                           "sum_that_day": 400}
            },
            filterText: "",
            startDate: "",
            endDate: ""
        }
        updateFilterVal = updateFilterVal.bind(this)
    }

    convertDate(dateString) {
        console.log("dateStr", dateString);
        var parts = dateString.split('.');
        return new Date(parts[2], parts[1] - 1, parts[0]);
    }

    checkDateFilter(currentDate, startDate, endDate){
        console.log("checkDF", this.convertDate(currentDate), startDate, endDate)
        return startDate < this.convertDate(currentDate) && this.convertDate(currentDate) < endDate
    }

    render() {
        var filteredItems = this.state.items.filter(item => item[1].includes(this.state.filterText) || item[3].includes(this.state.filterText) || item[4].includes(this.state.filterText))
        // console.log("checking", filteredItems[0][1], this.state.startDate, this.state.endDate)
        if(this.state.startDate && this.state.endDate) {
            filteredItems = filteredItems.filter(item => this.checkDateFilter(item[1], this.state.startDate, this.state.endDate))
        }
        return (
            <div>
                <table>
                    <tbody>
                {
                    filteredItems.map((item, index) => <DonationElem parentState={this.state}
                                                                    string={item} key={index} />)
                }
                    </tbody>
                </table>
            </div>
        );
    }
}


class DonationElem extends React.Component {

    displayRow(row){
        return row.map((cell) => <td key={this.props.key + cell.toString()}>{cell}</td>)
    }


    displaySpan(row){
        if(row === this.props.parentState.items.find((i) => i[1] === row[1])){
            let day_don= this.props.parentState.donationsPDay[row[1]]
            return <td rowSpan={day_don["donations_that_day"]}>{day_don["sum_that_day"]}</td>;
        }
    }


    render(){
        return(
            <React.Fragment>
                {<tr key={this.props.key}>{this.displayRow(this.props.string)}
                    {this.displaySpan(this.props.string)}
                </tr>}
            </React.Fragment>
        );
    }

}


export default App;