import React from 'react';
// import logo from './logo.svg';
import './App.css';

function App() {
    return (
        <div className="App">
            <header className="App-header">
            {/*<img src={logo} className="App-logo" alt="logo" />*/}
                <ListElem />
            </header>
        </div>
    );
}


class ListElem extends React.Component {
    // add State
  //
  //   componentDidMount() {
  //   fetch("https://0.0.0.0/api/getList")
  //     .then(res => res.json())
  //     .then(
  //       (result) => {
  //         this.setState({
  //           isLoaded: true,
  //           items: result.items
  //         });
  //       },
  //       // Note: it's important to handle errors here
  //       // instead of a catch() block so that we don't swallow
  //       // exceptions from actual bugs in components.
  //       (error) => {
  //         this.setState({
  //           isLoaded: true,
  //           error
  //         });
  //       }
  //     )
  // }

    render() {
        return (
            <div>
                {exampleElements.map((elem) => <DonationElem name={elem.name} key={elem.toString()} />)}
            </div>
        );
    }
}


class DonationElem extends React.Component {
    render(){
        return(
            <div>
                {this.props.name}
            </div>
        );
    }

}


const exampleElements = [
    {rows}
]

export default App;
