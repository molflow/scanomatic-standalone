import { shallow } from 'enzyme';
import React from 'react';

import '../components/enzyme-setup';
import RootContainer from '../../ccc/containers/RootContainer';
import cccMetadata from '../fixtures/cccMetadata';
import FakePromise from '../helpers/FakePromise';

describe('<RootContainer />', () => {
  let api;

  beforeEach(() => {
    api = {
      InitiateCCC: jasmine.createSpy('InitiateCCC').and.returnValue(new FakePromise()),
      finalizeCalibration: jasmine.createSpy('finalizeCalibration').and.returnValue(new FakePromise()),
    };
  });

  const createWrapper = () => shallow(<RootContainer api={api} />);

  it('should render <Root />', () => {
    const wrapper = createWrapper();
    expect(wrapper.find('Root').exists()).toBeTruthy();
  });

  it('should pass an empty cccMetadata', () => {
    const wrapper = createWrapper();
    expect(wrapper.prop('cccMetadata')).toBeFalsy();
  });

  it('should update the error on onError', () => {
    const wrapper = createWrapper();
    wrapper.prop('onError')('foobar');
    wrapper.update();
    expect(wrapper.prop('error')).toEqual('foobar');
  });

  const {
    species, reference, fixtureName, pinningFormat,
  } = cccMetadata;

  const cccData = {
    identifier: cccMetadata.id,
    access_token: cccMetadata.accessToken,
  };

  it('should call InitiateCCC on onInitializeCCC', () => {
    const wrapper = createWrapper();
    wrapper.prop('onInitializeCCC')(species, reference, fixtureName, pinningFormat);
    expect(api.InitiateCCC).toHaveBeenCalledWith(species, reference);
  });

  it('should set the error prop if initializing the CCC fails', () => {
    api.InitiateCCC.and.returnValue(FakePromise.reject('You broke biology'));
    const wrapper = createWrapper();
    wrapper.prop('onInitializeCCC')(species, reference, fixtureName, pinningFormat);
    wrapper.update();
    expect(wrapper.prop('error'))
      .toContain('Error initializing calibration: You broke biology');
  });

  describe('when Initializing the calibration succeeds', () => {
    beforeEach(() => {
      api.InitiateCCC.and.returnValue(FakePromise.resolve(cccData));
    });

    function initializeCCC(wrapper) {
      wrapper.prop('onInitializeCCC')(species, reference, fixtureName, pinningFormat);
    }

    it('should populate the cccMetadata prop', () => {
      const wrapper = createWrapper();
      initializeCCC(wrapper);
      wrapper.update();
      expect(wrapper.prop('cccMetadata')).toEqual(cccMetadata);
    });

    it('should clear the error prop', () => {
      const wrapper = createWrapper();
      wrapper.setState({ error: 'foobar' });
      initializeCCC(wrapper);
      wrapper.update();
      expect(wrapper.prop('error')).toBeFalsy();
    });

    it('should finalize the CCC on onFinalizeCCC', () => {
      const wrapper = createWrapper();
      initializeCCC(wrapper);
      wrapper.prop('onFinalizeCCC')();
      expect(api.finalizeCalibration)
        .toHaveBeenCalledWith(cccMetadata.id, cccMetadata.accessToken);
    });

    it('should set the error if finalization fails', () => {
      api.finalizeCalibration.and.returnValue(FakePromise.reject('Wobbly'));
      const wrapper = createWrapper();
      initializeCCC(wrapper);
      wrapper.prop('onFinalizeCCC')();
      wrapper.update();
      expect(wrapper.prop('error')).toEqual('Finalization error: Wobbly');
    });

    it('should set finalized to true if finalization succeeds', () => {
      api.finalizeCalibration.and.returnValue(FakePromise.resolve());
      const wrapper = createWrapper();
      initializeCCC(wrapper);
      wrapper.prop('onFinalizeCCC')();
      wrapper.update();
      expect(wrapper.prop('finalized')).toBeTruthy();
    });
  });
});
