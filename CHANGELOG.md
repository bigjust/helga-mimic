# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.4.11.1] - 2018-12-09]
### Fixed
- don't mimic reply for commands

## [0.4.10] - 2017-09-13]
### Fixed
- syntax issue when matching nicks

## [0.4.9] - 2017-09-10]
## Added
- Exception logging for generate_models in separate thread

## [0.4.8] - 2017-09-10]
### Fixed
- build markov file for channel

## [0.4.7] - 2017-09-08]
### Fixed
- bad indent led to cobe responses to not output if not replacing matched aliases

## [0.4.6] - 2017-09-08]
### Changed
- when replying to a ping, address the nick who pinged, not another nick
### Fixed
- fix regression where cobe brain wasn't being built on command

## [0.4.5] - 2017-09-07]
### Changed
- chain all alias markov models for associated nick

## [0.4.4] - 2017-08-30]
### Fixed

- use seperate thread for markov models
- fix regression in 'no models found' handling
- fix regression in regex handling message exclusions being ignored
- DRY markov file generation

## [0.4.3] - 2017-08-30]
### Fixed
- fixed filename for externally loaded models

## [0.4.2] - 2017-08-30]
### Changed
- store markov chains as files

## [0.4.1] - 2017-08-27]
### Added
- subcommand for tweeted last response
### Changed
- using Plugin subclass

## [0.4.0] - 2017-08-23]
### Added
- subcommand for loading external corpora
- setting for cobe reply time
### Changed
- improved corpus filter

## [0.3.1] - 2017-05-14]
### Added
- added a function for filtering messages into the markov chains

## [0.3.0] - 2017-04-16]
### Added
- use helga-alias to generate more complete models

## [0.2.2] - 2017-04-15]
### Added
- support for ignore list setting
- post processing of cobe generated replies
### Changed
- use cobe for channel-wide mimic, much faster

## [0.2.1] - 2017-04-08]
### Added
- added a method for other plugins to use helga-mimic to generate replies

## [0.2.0] - 2016-12-04]
### Added
- added cobe module to make some conversation
- added a temporary command ("!mimic build") to rebuild the brain

## [0.1.5] - 2016-11-19]
### Changed
- cleaned up some logging
- fixed some unit tests

## [0.1.4] - 2016-11-19]
### Changed
- no argument suppplied means to mimic current channel
- can specify multiple nicks

## [0.1.3] - 2016-11-17
### Figured Out
- I suck at deploying

## [0.1.2] - 2016-11-17
### Added
- setting to allow to change number of tries

## [0.1.1] - 2016-11-13
### Changed
- increased number of tries from 3 to 50
- allow anyone to call mimic

## [0.1.0] - 2016-11-13
### Added
- allow operators to generate mimics based on oral history
