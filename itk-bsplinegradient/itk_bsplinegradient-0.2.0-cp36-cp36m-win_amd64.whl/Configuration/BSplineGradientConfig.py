depends = ('ITKPyBase', 'ITKMesh', 'ITKImageGrid', 'ITKCommon', )
templates = (
  ('BSplineGradientImageFilter', 'itk::BSplineGradientImageFilter', 'itkBSplineGradientImageFilterISS2FF', True, 'itk::Image< signed short,2 >,float,float'),
  ('BSplineGradientImageFilter', 'itk::BSplineGradientImageFilter', 'itkBSplineGradientImageFilterIUC2FF', True, 'itk::Image< unsigned char,2 >,float,float'),
  ('BSplineGradientImageFilter', 'itk::BSplineGradientImageFilter', 'itkBSplineGradientImageFilterIUS2FF', True, 'itk::Image< unsigned short,2 >,float,float'),
  ('BSplineGradientImageFilter', 'itk::BSplineGradientImageFilter', 'itkBSplineGradientImageFilterIF2FF', True, 'itk::Image< float,2 >,float,float'),
  ('BSplineGradientImageFilter', 'itk::BSplineGradientImageFilter', 'itkBSplineGradientImageFilterISS3FF', True, 'itk::Image< signed short,3 >,float,float'),
  ('BSplineGradientImageFilter', 'itk::BSplineGradientImageFilter', 'itkBSplineGradientImageFilterIUC3FF', True, 'itk::Image< unsigned char,3 >,float,float'),
  ('BSplineGradientImageFilter', 'itk::BSplineGradientImageFilter', 'itkBSplineGradientImageFilterIUS3FF', True, 'itk::Image< unsigned short,3 >,float,float'),
  ('BSplineGradientImageFilter', 'itk::BSplineGradientImageFilter', 'itkBSplineGradientImageFilterIF3FF', True, 'itk::Image< float,3 >,float,float'),
  ('ImageToPointSetFilter', 'itk::ImageToPointSetFilter', 'itkImageToPointSetFilterISS2PSSS2', True, 'itk::Image< signed short,2 >, itk::PointSet < signed short,2 >'),
  ('ImageToPointSetFilter', 'itk::ImageToPointSetFilter', 'itkImageToPointSetFilterISS3PSSS3', True, 'itk::Image< signed short,3 >, itk::PointSet < signed short,3 >'),
  ('ImageToPointSetFilter', 'itk::ImageToPointSetFilter', 'itkImageToPointSetFilterIUC2PSUC2', True, 'itk::Image< unsigned char,2 >, itk::PointSet < unsigned char,2 >'),
  ('ImageToPointSetFilter', 'itk::ImageToPointSetFilter', 'itkImageToPointSetFilterIUC3PSUC3', True, 'itk::Image< unsigned char,3 >, itk::PointSet < unsigned char,3 >'),
  ('ImageToPointSetFilter', 'itk::ImageToPointSetFilter', 'itkImageToPointSetFilterIUS2PSUS2', True, 'itk::Image< unsigned short,2 >, itk::PointSet < unsigned short,2 >'),
  ('ImageToPointSetFilter', 'itk::ImageToPointSetFilter', 'itkImageToPointSetFilterIUS3PSUS3', True, 'itk::Image< unsigned short,3 >, itk::PointSet < unsigned short,3 >'),
  ('ImageToPointSetFilter', 'itk::ImageToPointSetFilter', 'itkImageToPointSetFilterIF2PSF2', True, 'itk::Image< float,2 >, itk::PointSet < float,2 >'),
  ('ImageToPointSetFilter', 'itk::ImageToPointSetFilter', 'itkImageToPointSetFilterIF3PSF3', True, 'itk::Image< float,3 >, itk::PointSet < float,3 >'),
)
snake_case_functions = ('b_spline_gradient_image_filter', 'image_to_point_set_filter', )
